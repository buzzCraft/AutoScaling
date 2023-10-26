from utils import get_min_max, get_running_servers, get_current_players
from openstackutils import OpenStackManager

class Scaler:
    """
    Scaler class to scale the game servers based on the scaling scheme.
    """
    def __init__(self,game, scaling_scheme, baseload, capacity_per_server):
        self.game = game
        self.scaling_scheme = scaling_scheme
        self.baseload = baseload
        self.capacity_per_server = capacity_per_server
        self.current_players = self.get_current_players()
        self.current_servers = self.get_running_servers()
        self.VMCONTROLLER = OpenStackManager()

    def get_current_players(self):
        return get_current_players(self.game)


    def get_running_servers(self):
        # Return the current number of running servers.
        return get_running_servers()

    def create_instance(self, instance_name, image_name, flavor_name, network_name):
        # Simulated method to create an instance. Replace with actual logic.
        print(f"Creating server instance: {instance_name}")
    
    def delete_instance(self, instance_name):
        # Simulated method to delete an instance. Replace with actual logic.
        print(f"Deleting server instance: {instance_name}")

    def scale(self):
        current_players = self.get_current_players(game=game)
        current_servers = self.get_running_servers()

        # Calculate required servers based on the current number of players and capacity per server
        required_servers = (current_players - self.baseload) // self.capacity_per_server
        if required_servers < 1:
            required_servers = 1
        
        # Scaling decision based on the scaling scheme
        if self.scaling_scheme == "some_method":
            # Implement the logic for this method
            pass
        # Add other scaling schemes as needed
        # elif self.scaling_scheme == "another_method":
        #     ...

        # Adjust the number of servers based on the decision
        if current_servers < required_servers:
            for _ in range(required_servers - current_servers):
                self.create_instance(instance_name, image_name, flavor_name, network_name)
        elif current_servers > required_servers:
            for _ in range(current_servers - required_servers):
                self.delete_instance(instance_name)