
from flask import Flask, Response, jsonify, request
from openstack_check import get_running_servers
from fake_servers import FakeServer
import logging

fake_servers = {}

logging.basicConfig(
    level=logging.WARNING,
    filename='server_status.log',  # Set the minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger('get_running_servers')

app = Flask(__name__)
logger.info("Starting OpenStack app")

@app.route('/metrics', methods=['GET'])
def metrics():
    # Get the count of "real" running servers
    real_running_servers = get_running_servers()

    # Initialize the response string with the real server count
    response_str = f"running_servers_total {real_running_servers}\n"

    # Add metrics for each fake server by gamename
    for gamename, fake_server in fake_servers.items():
        response_str += f"fake_servers_total{{gamename=\"{gamename}\"}} {fake_server.running_servers}\n"

    return Response(response_str, content_type="text/plain")

@app.route('/fakeserver/create/<gamename>', methods=['POST'])
def create_fakeserver(gamename):
    if gamename not in fake_servers:
        fake_servers[gamename] = FakeServer(gamename)
    return jsonify(fake_servers[gamename].getdata())

@app.route('/fakeserver/scaleup/<gamename>', methods=['POST'])
def scale_up(gamename):
    num_servers = request.json.get('num_servers', 1)  # Default to scaling up by 1
    if gamename in fake_servers:
        fake_servers[gamename].scale_up(num_servers)
        return jsonify(fake_servers[gamename].getdata())
    else:
        return jsonify({"error": "Fake server not found"}), 404

@app.route('/fakeserver/scaledown/<gamename>', methods=['POST'])
def scale_down(gamename):
    num_servers = request.json.get('num_servers', 1)  # Default to scaling down by 1
    if gamename in fake_servers:
        fake_servers[gamename].scale_down(num_servers)
        return jsonify(fake_servers[gamename].getdata())
    else:
        return jsonify({"error": "Fake server not found"}), 404
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
