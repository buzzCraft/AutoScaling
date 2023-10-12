from openstack import connection
import os




conn = connection.Connection(
    auth_url=os.getenv("OS_AUTH_URL"),
    project_name=os.getenv("OS_PROJECT_NAME"),
    username=os.getenv("OS_USERNAME"),
    password=os.getenv("OS_PASSWORD"),
    user_domain_id='default',
    project_domain_id='default')

def create_instance(instance_name, image_name, flavor_name, network_name):
    """Create a new VM instance."""
    
    image = conn.compute.find_image(image_name)
    flavor = conn.compute.find_flavor(flavor_name)
    network = conn.network.find_network(network_name)

    server = conn.compute.create_server(
        name=instance_name,
        image_id=image.id,
        flavor_id=flavor.id,
        networks=[{"uuid": network.id}]
    )
    
    server = conn.compute.wait_for_server(server)
    return server

def delete_instance(instance_name):
    """Shutdown and delete a VM instance."""
    
    server = conn.compute.find_server(instance_name)
    if server:
        conn.compute.delete_server(server)
    else:
        print(f"Instance {instance_name} not found!")

# Example usage:
# create_instance("new_VM_instance", "YOUR_IMAGE_NAME", "YOUR_FLAVOR_NAME", "YOUR_NETWORK_NAME")
# delete_instance("new_VM_instance")
