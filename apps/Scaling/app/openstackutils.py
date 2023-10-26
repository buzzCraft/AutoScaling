from openstack import connection
import os
import logging
logger = logging.getLogger('scaler')

class OpenStackManager:
    
    def __init__(self):
        self.conn = connection.Connection(
            auth_url=os.getenv("OS_AUTH_URL"),
            project_name=os.getenv("OS_PROJECT_NAME"),
            username=os.getenv("OS_USERNAME"),
            password=os.getenv("OS_PASSWORD"),
            user_domain_id='default',
            project_domain_id='default'
        )
        
    
    def create_instance(self, instance_name, image_name, flavor_name, network_name):
        """Create a new VM instance."""
        try:    
            image = self.conn.compute.find_image(image_name)
            flavor = self.conn.compute.find_flavor(flavor_name)
            network = self.conn.network.find_network(network_name)

            server = self.conn.compute.create_server(
                name=instance_name,
                image_id=image.id,
                flavor_id=flavor.id,
                networks=[{"uuid": network.id}]
            )
            
            server = self.conn.compute.wait_for_server(server)
            logger.info(f"Created server {server.name} with id {server.id}")
            return server
        except Exception as e:
            logger.error("Error starting new VM" + e)
            return None
    
def delete_instance(self):
    """Delete the most recently created VM instance."""
    try:
        # Fetch all servers
        servers = list(self.conn.compute.servers())
        
        # If no servers, nothing to delete
        if not servers:
            logger.info("No instances found!")
            return
        
        # Sort servers by created date
        newest_server = sorted(servers, key=lambda s: s.created_at, reverse=True)[0]
        
        # Delete the newest server
        self.conn.compute.delete_server(newest_server)
        logger.info(f"Deleted newest server {newest_server.name} with id {newest_server.id}")
    except Exception as e:
        logger.error(f"Error deleting newest VM: {e}")

# Usage:

# manager = OpenStackManager()
# manager.create_instance("instance_name", "image_name", "flavor_name", "network_name")
# manager.delete_instance("instance_name")
