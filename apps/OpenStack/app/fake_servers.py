class FakeServer:
    def __init__(self, gamename):
        self.gamename = gamename
        self.running_servers = 0

    def getdata(self):
        # Return a dict with the game name and the number of running servers
        return {"title": self.gamename, "running_servers": self.running_servers}
    
    def scale_up(self, num_servers):
        self.running_servers += num_servers

    def scale_down(self, num_servers):
        self.running_servers -= num_servers
        