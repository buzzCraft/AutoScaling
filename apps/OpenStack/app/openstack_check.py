
from openstack import connection
import os

def get_running_servers():
    conn = connection.Connection(auth_url=os.getenv("OS_AUTH_URL"),
                                 project_name=os.getenv("OS_PROJECT_NAME"),
                                 username=os.getenv("OS_USERNAME"),
                                 password=os.getenv("OS_PASSWORD"),
                                 user_domain_id='default',
                                 project_domain_id='default')

    servers = list(conn.compute.servers())
    running_servers = [server for server in servers if server.status == 'ACTIVE']
    return len(running_servers)

if __name__ == "__main__":
    print(get_running_servers())
