from openstack import connection
from utils import get_running_servers
import os
import logging
logger = logging.getLogger('scaler')
import dotenv
dotenv.load_dotenv()

class OpenStackManager:
    
    def __init__(self, game):
        # Add game name
        self.conn = connection.Connection(
            auth_url=os.getenv("OS_AUTH_URL"),
            project_name=os.getenv("OS_PROJECT_NAME"),
            username=os.getenv("OS_USERNAME"),
            password=os.getenv("OS_PASSWORD"),
            user_domain_id='default',
            project_domain_id='default'
        )
        self.image_name = os.getenv("IMAGE_NAME")
        self.flavor_name = os.getenv("FLAVOR_NAME")
        self.network_name = os.getenv("NETWORK_NAME")
        self.instance_base = os.getenv("INSTANCE_BASE")
        self.instance_base = f"{game}-{self.instance_base}"
        
    def scale_up_servers(self, num_servers):
        """Scale up the number of servers based on the given image."""
        num_servers = int(num_servers)
        running_servers = get_running_servers()
        for i in range(num_servers):
            instance_name = f"{self.instance_base}-{running_servers+1+i}"
            self.create_instance(instance_name)

    def scale_down_servers(self, num_servers):
        """Scale down the number of servers based on the given image."""
        num_servers = int(abs(num_servers))
        for i in range(num_servers):
            logger.info(f"Deleting server {i+1}")
            self.delete_instance()

    
    def create_instance(self, instance_name):
        """Create a new VM instance."""
        try:    
            image = self.conn.compute.find_image(self.image_name)
            flavor = self.conn.compute.find_flavor(self.flavor_name)
            network = self.conn.network.find_network(self.network_name)

            server = self.conn.compute.create_server(
                name=instance_name,
                image_id=image.id,
                flavor_id=flavor.id,
                networks=[{"uuid": network.id}]
            )
            
            server = self.conn.compute.wait_for_server(server)
            logger.info(f"Created server {server.name} with id {server.id}")
            return server.name
        except Exception as e:
            logger.error("Error starting new VM" + e)
            return None
        
    def delete_instance(self, instance_id):
        """Delete an instance and its attached volumes."""
        try:
            # Fetch all servers
            servers = list(self.conn.compute.servers())
            
            # Filter servers with the specified instance base name
            filtered_servers = [server for server in servers if self.instance_base in server.name]
            
            # If no matching servers, nothing to delete
            if not filtered_servers:
                logger.warning(f"No instances found with base name {self.instance_base}!")
                return
            
            # Sort filtered servers by created date
            instance_id = sorted(filtered_servers, key=lambda s: s.created_at, reverse=True)[0]
            instance = self.conn.compute.get_server(instance_id)

            # Retrieve and delete all attached volumes
            for volume_attachment in instance.volume_attachments:
                volume = self.conn.block_storage.get_volume(volume_attachment["volumeId"])
                self.conn.block_storage.delete_volume(volume, ignore_missing=False)
                logger.info(f"Deleted volume {volume.id}")

            # Now delete the instance
            self.conn.compute.delete_server(instance_id)
            logger.info(f"Deleted instance {instance_id}")

        except Exception as e:
            logger.error(f"Error in deleting instance or its volumes: {e}")



if __name__ == "__main__":
    osm = OpenStackManager("Test")
    inp = ""
    while inp != "Q":
        inp = input("Scale [U]p or [D]own?")
        if inp == "U":
            osm.scale_up_servers(1)
        elif inp == "D":
            osm.scale_down_servers(1)
        else:
            print("Invalid input")
