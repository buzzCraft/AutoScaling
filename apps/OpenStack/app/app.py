from fastapi import FastAPI, Response, HTTPException
from openstack_check import get_running_servers
from fake_servers import FakeServer
import logging
from typing import Dict

app = FastAPI()

fake_servers: Dict[str, FakeServer] = {}

logging.basicConfig(
    level=logging.WARNING,
    filename='server_status.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger('get_running_servers')
logger.info("Starting OpenStack app")

@app.get("/metrics")
def metrics():
    response_str = "running_servers_total {}\n".format(get_running_servers())

    for gamename, fake_server in fake_servers.items():
        response_str += 'fake_servers_total{{gamename="{}"}} {}\n'.format(gamename, fake_server.running_servers)

    return Response(content=response_str, media_type="text/plain")

@app.post("/fakeserver/create/{gamename}")
def create_fakeserver(gamename: str):
    if gamename not in fake_servers:
        fake_servers[gamename] = FakeServer(gamename)
    return fake_servers[gamename].getdata()

@app.post("/fakeserver/scaleup/{gamename}")
def scale_up(gamename: str):
    if gamename in fake_servers:
        fake_servers[gamename].scale_up(1)
        return fake_servers[gamename].getdata()
    raise HTTPException(status_code=404, detail="Fake server not found")

@app.post("/fakeserver/scaledown/{gamename}")
def scale_down(gamename: str):
    if gamename in fake_servers:
        fake_servers[gamename].scale_down(1)
        return fake_servers[gamename].getdata()
    raise HTTPException(status_code=404, detail="Fake server not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)