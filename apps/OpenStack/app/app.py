
from flask import Flask, Response
from openstack_check import get_running_servers
import logging

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
    running_servers = get_running_servers()
    response_str = f"running_servers_total {running_servers}\n"
    return Response(response_str, content_type="text/plain")
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
