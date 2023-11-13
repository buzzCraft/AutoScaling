from utils import get_min_max, get_running_servers, get_current_players
from openstackutils import OpenStackManager
from fakeserver import FakeServer
import datetime
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
        logger.info(f"Current players: {current_players}, Current servers: {current_servers}")

        
        # Scaling decision based on the scaling scheme
        if self.scaling_scheme == 1:
            required_servers = self.scaling_1(current_servers, current_players)
        elif self.scaling_scheme == 2:
            required_servers = self.scaling_2(current_servers, current_players,s_up=80, s_down=75)
        else:
            required_servers = self.scaling_1(current_servers, current_players)
        logger.info(f"Required servers: {required_servers}")

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
        
    def scaling_based_on_derivative(self, current_servers, current_players):
        """
        Scale servers based on the rate of change of player count (derivative).

        :param current_servers: The current number of servers.
        :param current_players: The current number of players.
        :param time_delta: The time passed since the last measurement in minutes.
        :return: The number of servers to scale up or down.
        """
        now = datetime.datetime.now()
        time_delta = (now - self.previous_time).total_seconds() / 60
        self.previous_time = now
        # Calculate the rate of change of player count
        player_change_rate = (current_players - self.previous_player_count) / time_delta

        # Define thresholds for scaling
        SCALE_UP_THRESHOLD = 0.8  # Scale up if server is at 80% capacity
        SCALE_DOWN_THRESHOLD = 0.4  # Scale down if server is below 40% capacity

        # Calculate the current load percentage
        capacity_percentage = self.calc_capacity(current_servers, current_players)

        required_servers = 0

        # If player count is increasing rapidly, scale up more aggressively
        if player_change_rate > 0 and capacity_percentage > SCALE_UP_THRESHOLD:
            # Calculate additional servers needed based on rate of player increase
            required_servers = int(player_change_rate * self.server_capacity)  # Assuming 'server_capacity' is a known value

        # If player count is decreasing, consider scaling down
        elif player_change_rate < 0 and capacity_percentage < SCALE_DOWN_THRESHOLD and current_servers > 1:
            # Calculate the number of servers that can be removed based on rate of player decrease
            required_servers = -int(abs(player_change_rate) * self.server_capacity)

        # Ensure we do not scale down below 1 server or exceed the max number of servers
        required_servers = max(-current_servers + 1, required_servers)  # Don't go below 1 server
        required_servers = min(self.number_of_servers - current_servers, required_servers)  # Don't exceed max servers

        return required_servers


        
    
