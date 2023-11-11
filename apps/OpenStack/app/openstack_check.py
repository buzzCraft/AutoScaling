from openstack import connection
import os
# import logging

# logger = logging.getLogger('get_running_servers')
auth_url=os.getenv("OS_AUTH_URL")
project_name=os.getenv("OS_PROJECT_NAME")
username=os.getenv("OS_USERNAME")
password=os.getenv("OS_PASSWORD")

def get_running_servers():
    running_servers = ""
    try:
        # Use a context manager to ensure the connection is properly closed
        with connection.Connection(auth_url=auth_url,
                                   project_name=project_name,
                                   username=username,
                                   password=password,
                                   user_domain_id='default',
                                   project_domain_id='default') as conn:

            servers = list(conn.compute.servers())
            running_servers = [server for server in servers if server.status == 'ACTIVE']
            return len(running_servers) - 1

    except Exception as e:
        # logger.error(e)
        return -1

    


if __name__ == "__main__":
    print(get_running_servers())
    print("Done!")
