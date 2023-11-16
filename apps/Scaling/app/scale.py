from utils import get_min_max, get_running_servers, get_current_players
from openstackutils import OpenStackManager
from fakeserver import FakeServer
import datetime
import math
import logging
logger = logging.getLogger('scaler')

class Scaler:
    """
    Scaler class to scale the game servers based on the scaling scheme.
    """
    def __init__(self,game, scaling_scheme, baseload, capacity_per_server,server_suffix, number_of_servers, fake=False):
        """
        scaling_scheme: 1 = Scale based on current players
                        2 = Scale based on current players and time of day
                        3 = Scale based on current players and derivative of player count

        """

        self.game = game
        self.scaling_scheme = int(scaling_scheme)
        self.baseload = baseload
        self.capacity_per_server = int(capacity_per_server)
        self.server_name = f"{game} {server_suffix}"
        self.number_of_servers = number_of_servers

        # Just init to something
        self.current_players = 1000
        self.current_players = int(self.get_current_players())
        self.previous_player_count = self.current_players
        self.previous_time = datetime.datetime.now()
        
        self.fake = fake
        if self.fake:
            self.VMCONTROLLER = FakeServer(gamename=self.server_name)
            self.current_servers = self.VMCONTROLLER.get_servers()
        else:
            self.VMCONTROLLER = OpenStackManager(game)
            self.current_servers = int(self.get_running_servers())

    def get_current_players(self):
        cur_player = get_current_players(self.game)
        # Fix for the data not being updated
        if cur_player != 0:
            self.current_players = cur_player
        return self.current_players
        
    


    def get_running_servers(self):
        # Return the current number of running servers.
        if self.fake == True:
            return self.VMCONTROLLER.get_servers()
        return get_running_servers()

    def create_instance(self, nr_of_servers):
        self.VMCONTROLLER.scale_up_servers(nr_of_servers)

    
    def delete_instance(self, nr_of_servers):
        self.VMCONTROLLER.scale_down_servers(nr_of_servers)
        logger.info(f"Deleted {nr_of_servers} server instances")


    def scale(self):
        current_players = self.get_current_players()
        current_servers = self.get_running_servers()
        required_servers = 0
        logger.info(f"Current players: {current_players}, Current servers: {current_servers}, Scaling scheme: {self.scaling_scheme}, server capacity: {self.capacity_per_server*current_servers}, Baseload: {self.baseload}")

        
        # Scaling decision based on the scaling scheme
        if self.scaling_scheme == 1:
            required_servers = self.scaling_1(current_servers, current_players)
        elif self.scaling_scheme == 2:
            required_servers = self.scaling_2(current_servers, current_players,s_up=80, s_down=75)
        elif self.scaling_scheme == 3:
            required_servers = self.scaling_3(current_servers, current_players,s_up=80, s_down=75)
        else:
            required_servers = self.scaling_1(current_servers, current_players)
        logger.info(f"Required servers: {required_servers}")

        # Ensure that we do not scale above the maximum number of servers
        if required_servers + current_servers > self.number_of_servers:
            required_servers = self.number_of_servers
        # Ensure that we do not scale below 1 server
        elif required_servers + current_servers < 1:
            required_servers = 1

        if required_servers > 0:            
            self.create_instance(required_servers)
        elif required_servers < 0:
            self.delete_instance(required_servers)

    def calc_capacity(self, current_servers, current_players):
        # Calculate the capacity of the current number of servers
        # Calculate the current capacity
        logger.debug(f"Current players: {current_players}")
        logger.debug(f"Current servers: {current_servers}")
        current_players = int(current_players) - self.baseload
        try:
            current_capacity = (int(current_servers) * self.capacity_per_server)
        except:
            current_capacity = 0
        # Based on current players, calculate the target capacity
        target_capacity = current_players
        # Calculate the percentage of capacity
        if current_capacity == 0:
            current_capacity = 1000
        capacity_percentage = target_capacity / current_capacity * 100
        logger.debug(f"Current players above baseload: {current_players}")
        logger.debug(f"Current capacity: {current_capacity}")
        logger.debug(f"Target capacity: {target_capacity}")
        logger.debug(f"Baseline: {self.baseload}")
        logger.debug(f"Current capacity: {capacity_percentage}")

        # Make sure that the percentage is not above bellow 0% or above 200%
        if capacity_percentage < 0:
            capacity_percentage = 0
        elif capacity_percentage > 200:
            capacity_percentage = 200
        

        return capacity_percentage

    def scaling_1(self, current_servers, current_players):
        """
        Scale based on current players
        Scale up if servers are on 80% capacity
        Scale down if servers are on 50% capacity
        """
        logger.debug(f"Scaling scheme 1")
        required_servers = 0
        capacity_percentage = self.calc_capacity(current_servers, current_players)

        # Scale up if above 80% capacity
        while capacity_percentage > 80:
            required_servers += 1
            if required_servers + current_servers >= self.number_of_servers:
                break
            capacity_percentage = self.calc_capacity(current_servers + required_servers, current_players)

        # Scale down if below 40% capacity but ensure that we do not scale down below 1 server
        while capacity_percentage < 40 and current_servers + required_servers > 1:
            required_servers -= 1
            if required_servers + current_servers <= 1:
                break
            new_capacity_percentage = self.calc_capacity(current_servers + required_servers, current_players)
            # If scaling down once would bring us above 40%, we check to see if we should scale down
            if new_capacity_percentage >= 40:
                break  # We've reached an optimal number of servers
            capacity_percentage = new_capacity_percentage
        logger.debug(f"New capacity: {capacity_percentage}")     
        logger.debug(f"Required servers: {required_servers}")
        return required_servers
    
    def scaling_2(self, current_servers, current_players, s_up=80, s_down=40):
        """
        Scale based on current players
        Scale up if servers are on s_up capacity
        Scale down if servers are on s_down capacity, but not below s_up capacity

        """
        logger.debug("Scaling scheme 2")
        required_servers = 0
        capacity_percentage = self.calc_capacity(current_servers, current_players)

        # Scale up if above s_up% capacity
        while capacity_percentage > s_up:
            required_servers += 1
            if required_servers + current_servers >= self.number_of_servers:
                break
            capacity_percentage = self.calc_capacity(current_servers + required_servers, current_players)

        # Scale down if below s_down capacity, but not below s_up capacity
        while capacity_percentage < s_down and current_servers + required_servers > 1:
            required_servers -= 1
            new_capacity_percentage = self.calc_capacity(current_servers + required_servers, current_players)
            if new_capacity_percentage >= s_up:
                required_servers += 1  # Go one step back up
                break  # Stop scaling down if we reach or exceed the s_up threshold
            elif current_servers + required_servers < 1:
                required_servers += 1  # Ensure we don't go below 1 server
                break
            capacity_percentage = new_capacity_percentage

        logger.debug(f"New capacity: {capacity_percentage}")     
        logger.debug(f"Required servers: {required_servers}")
        return required_servers
        
    def scaling_3(self, current_servers, current_players, s_up=80, s_down=40):
        """
        Scale servers based on the rate of change of player count (derivative).

        :param current_servers: The current number of servers.
        :param current_players: The current number of players.
        :param time_delta: The time passed since the last measurement in minutes.
        :return: The number of servers to scale up or down.
        """
        required_servers = 0
        now = datetime.datetime.now()
        time_delta = (now - self.previous_time).total_seconds() / 60
        self.previous_time = now
        # Calculate the rate of change of player count
        player_change_rate = (current_players - self.previous_player_count) / time_delta

        # Predict player count in 5 minutes
        predicted_player_count = current_players + player_change_rate

        # Calculate the current load percentage
        capacity_percentage = self.calc_capacity(current_servers, predicted_player_count)

        while capacity_percentage > s_up:
            required_servers += 1
            if required_servers + current_servers >= self.number_of_servers:
                break
            capacity_percentage = self.calc_capacity(current_servers + required_servers, predicted_player_count)

                # Scale down if below s_down capacity, but not below s_up capacity
        while capacity_percentage < s_down and current_servers + required_servers > 1:
            required_servers -= 1
            new_capacity_percentage = self.calc_capacity(current_servers + required_servers, predicted_player_count)
            if new_capacity_percentage >= s_up:
                required_servers += 1  # Go one step back up
                break  # Stop scaling down if we reach or exceed the s_up threshold
            elif current_servers + required_servers < 1:
                required_servers += 1  # Ensure we don't go below 1 server
                break
            capacity_percentage = new_capacity_percentage

        logger.debug(f"New capacity: {capacity_percentage}")     
        logger.debug(f"Required servers: {required_servers}")
        return required_servers
    
    def scaling_4(self, current_servers, current_players, free_spots=1000):
        """
        Scale on free player spots instead of server capacity %
        """

        required_servers = 0
        # Calculate the current server status
        current_capacity = (int(current_servers) * self.capacity_per_server)
        current_free_spots = current_capacity - current_players
        logger.debug(f"Current free spots: {current_free_spots}")
        # Calculate the target capacity
        target_capacity = current_players + free_spots
        # Calculate the required servers
        required_servers = (target_capacity - current_capacity) / self.capacity_per_server
        # Round up to the nearest integer
        required_servers = math.ceil(required_servers)
        logger.debug(f"Required servers: {required_servers}")
        return required_servers
    
    def scaling_5(self, current_servers, current_players, free_spots=1000):
        """
        Combine scaling 3 and 4
        Calculate free spots based on the derivative of player count
        """
        required_servers = 0
        now = datetime.datetime.now()
        time_delta = (now - self.previous_time).total_seconds() / 60
        self.previous_time = now
        # Calculate the rate of change of player count
        player_change_rate = (current_players - self.previous_player_count) / time_delta
        # New capacity is player count + free spots + rate of change
        new_capacity = current_players + free_spots + player_change_rate

        return self.scaling_4(current_servers, new_capacity, free_spots=free_spots)

        


        
    
