from utils import get_min_max, get_running_servers, get_current_players
from openstackutils import OpenStackManager

class Scaler:
    """
    Scaler class to scale the game servers based on the scaling scheme.
    """
    def __init__(self,game, scaling_scheme, baseload, capacity_per_server):
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
        self.current_servers = int(self.get_running_servers())
        self.VMCONTROLLER = OpenStackManager()

    def get_current_players(self):
        return get_current_players(self.game)


    def get_running_servers(self):
        # Return the current number of running servers.
        return get_running_servers()

    def create_instance(self, nr_of_servers):
        server = self.VMCONTROLLER.scale_up_servers(nr_of_servers)
        print(f"Creating server instance: {server}")

    
    def delete_instance(self, nr_of_servers):
        server = self.VMCONTROLLER.delete_instance(nr_of_servers)
        print(f"Deleting server instance: {server}")

    def scale(self):
        current_players = self.get_current_players()
        current_servers = self.get_running_servers()
        required_servers = 0
        print(f"Current players: {current_players}, Current servers: {current_servers}")
        
        # Scaling decision based on the scaling scheme
        if self.scaling_scheme == 1:
            required_servers = self.scaling_1(current_servers, current_players)
            print(f"Required servers: {required_servers}")
            print(type(required_servers))
        if required_servers < 0:            
            self.create_instance(required_servers)
        elif required_servers > 0:
            self.delete_instance(required_servers)

    def calc_capacity(self, current_servers, current_players):
        # Calculate the capacity of the current number of servers
        # Calculate the current capacity
        print(f"Current servers: {current_servers}")
        print(f"Capacity per server: {self.capacity_per_server}")

        current_capacity = (int(current_servers) * self.capacity_per_server) + self.baseload
        # Based on current players, calculate the target capacity
        target_capacity = current_players - self.baseload
        # Calculate the percentage of capacity
        capacity_percentage = target_capacity / current_capacity * 100
        print(f"Current players: {current_players}")
        print(f"Current capacity: {current_capacity}")
        print(f"Target capacity: {target_capacity}")
        print(f"Baseline: {self.baseload}")
        print(f"Current capacity: {capacity_percentage}")
        return capacity_percentage

    def scaling_1(self, current_servers, current_players):
        """
        Scale based on current players
        Scale up if servers are on 80% capacity
        Scale down if servers are on 50% capacity
        """
        required_servers = 0
        capacity_percentage = self.calc_capacity(current_servers, current_players)
        # If above 80, scale up with one server and check again untill we go belov 80%
        while capacity_percentage > 80:
            required_servers += 1
            capacity_percentage = self.calc_capacity(current_servers+required_servers, current_players)

        # If below 50, scale down with one server and check again untill we go above 50%
        while capacity_percentage < 50:
            required_servers -= 1
            capacity_percentage = self.calc_capacity(current_servers+required_servers, current_players)
        return required_servers
    
