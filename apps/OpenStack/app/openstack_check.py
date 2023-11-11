from openstack import connection
import os

# Assuming logging is properly configured
import logging
logger = logging.getLogger('get_running_servers')

auth_url = os.getenv("OS_AUTH_URL")
project_name = os.getenv("OS_PROJECT_NAME")
username = os.getenv("OS_USERNAME")
password = os.getenv("OS_PASSWORD")

def get_running_servers():
    try:
        conn = connection.Connection(auth_url=auth_url,
                                     project_name=project_name,
                                     username=username,
                                     password=password,
                                     user_domain_id='default',
                                     project_domain_id='default')
        
        active_servers_count = 0
        for server in conn.compute.servers():
            if server.status == 'ACTIVE':
                active_servers_count += 1

        conn.close()
        return active_servers_count - 1

    except Exception as e:
        logger.error("Error in get_running_servers: {}".format(e))
        return -1

if __name__ == "__main__":
    print(get_running_servers())
    print("Done!")
