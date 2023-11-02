import requests


# Create a fake serverstack for a game
class FakeServer:
    def __init__(self, gamename, max_servers=10):
        self.max_servers = max_servers
        self.gamename = gamename
        self.servers = 0
        self.create_fakeserver()

    def scale_up_servers(self, nr_of_servers):
        for i in range(abs(nr_of_servers)):
            self.scale_up()

    def scale_down_servers(self, nr_of_servers):
        for i in range(abs(nr_of_servers)):
            self.scale_down()

    def create_fakeserver(self):
        url = f"http://10.196.37.200:5000/fakeserver/create/{self.gamename}"
        response = requests.post(url)
        return response.json()

    def scale_up(self):
        url = f"http://10.196.37.200:5000/fakeserver/scaleup/{self.gamename}"
        response = requests.post(url)
        return response.json()

    def scale_down(self):
        url = f"http://10.196.37.200:5000/fakeserver/scaledown/{self.gamename}"
        response = requests.post(url)
        return response.json()