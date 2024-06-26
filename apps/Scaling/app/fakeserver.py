import requests
import logging
logger = logging.getLogger('scaler')

# Create a fake serverstack for a game
class FakeServer:
    def __init__(self, gamename, max_servers=10):
        self.max_servers = max_servers
        self.gamename = gamename
        self.servers = 0
        self.server_address = "http://10.196.37.200:5000"
        self.create_fakeserver()
        

    def scale_up_servers(self, nr_of_servers):
        logger.info(f"Scaling up {nr_of_servers} fake servers")
        for i in range(abs(nr_of_servers)):
            self.scale_up()
            self.servers += 1

    def scale_down_servers(self, nr_of_servers):
        logger.info(f"Scaling down {nr_of_servers} fake servers")
        for i in range(abs(nr_of_servers)):
            self.scale_down()
            self.servers -= 1

    def create_fakeserver(self):
        url = f"{self.server_address}/fakeserver/create/{self.gamename}"
        response = requests.post(url)
        logger.debug(response.json())
        return response.json()

    def scale_up(self):
        url = f"{self.server_address}/fakeserver/scaleup/{self.gamename}"
        response = requests.post(url)
        logger.debug(response.json())
        return response.json()

    def scale_down(self):
        url = f"{self.server_address}/fakeserver/scaledown/{self.gamename}"
        response = requests.post(url)
        logger.debug(response.json())
        return response.json()
    
    def get_servers(self):
        url = f"{self.server_address}/fakeserver/{self.gamename}"
        response = requests.post(url)
        data = response.json()
        number_of_servers = data['running_servers']
        self.servers = int(number_of_servers)

        return int(number_of_servers)


