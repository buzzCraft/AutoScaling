from utils import get_min_max, get_running_servers, get_current_players
from openstackutils import OpenStackManager
from fakeserver import FakeServer
import logging
logger = logging.getLogger('scaler')
class Scaler:
    """
    Scaler class to scale the game servers based on the scaling scheme.
    """
    def __init__(self,game, scaling_scheme, baseload, capacity_per_server, fake=False):
        """
        scaling_scheme: 1 = Scale based on current players
                        2 = Scale based on current players and time of day
                        3 = Scale based on current players and derivative of player count

        """

        self.game = game
        self.scaling_scheme = int(scaling_scheme)
        self.baseload = baseload
        self.capacity_per_server = int(capacity_per_server)
        self.current_players = int(self.get_current_players())
        
        self.fake = fake
        if self.fake:
            self.VMCONTROLLER = FakeServer(gamename=game)
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
        current_capacity = (int(current_servers) * self.capacity_per_server)
        # Based on current players, calculate the target capacity
        target_capacity = current_players
        # Calculate the percentage of capacity
        if current_capacity == 0:
            capacity_percentage = 100
        else:
            capacity_percentage = target_capacity / current_capacity * 100
        logger.debug(f"Current players above baseload: {current_players}")
        logger.debug(f"Current capacity: {current_capacity}")
        logger.debug(f"Target capacity: {target_capacity}")
        logger.debug(f"Baseline: {self.baseload}")
        logger.debug(f"Current capacity: {capacity_percentage}")
        

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
            if required_servers + current_servers == 7:
                break
            capacity_percentage = self.calc_capacity(current_servers + required_servers, current_players)

        # Scale down if below 50% capacity but ensure that we do not scale down below 1 server
        while capacity_percentage < 40 and current_servers + required_servers > 1:
            required_servers -= 1
            if required_servers + current_servers == 1:
                break
            new_capacity_percentage = self.calc_capacity(current_servers + required_servers, current_players)
            # If scaling down once would bring us above 50%, we check to see if we should scale down
            if new_capacity_percentage >= 40:
                break  # We've reached an optimal number of servers
            capacity_percentage = new_capacity_percentage
        logger.debug(f"New capacity: {capacity_percentage}")     
        logger.debug(f"Required servers: {required_servers}")
        return required_servers

        
    
