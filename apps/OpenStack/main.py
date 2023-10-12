import subprocess
import time

def get_running_servers_count():
    """Get the number of running servers on the OpenStack cloud."""

    # Use the 'openstack server list' command to get a list of all servers
    result = subprocess.run(['openstack', 'server', 'list', '--status', 'ACTIVE', '-c', 'ID', '-f', 'value'], capture_output=True, text=True)

    # Split the result by lines to get the number of active servers
    active_servers = result.stdout.splitlines()

    return len(active_servers)

def main(interval):
    """Main function to check the number of running servers at regular intervals."""

    while True:
        count = get_running_servers_count()
        print(f"{count} servers are currently running.")
        
        # Sleep for the specified interval before checking again
        time.sleep(interval)

if __name__ == "__main__":
    # Set the interval (in seconds) at which to check the number of running servers
    INTERVAL = 300  # e.g., 300 seconds (5 minutes)
    
    main(INTERVAL)