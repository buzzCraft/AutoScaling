
from flask import Flask, Response
from openstack_check import get_running_servers

app = Flask(__name__)

@app.route('/metrics', methods=['GET'])
def metrics():
    running_servers = get_running_servers()
    response_str = f"running_servers_total {running_servers}\n"
    return Response(response_str, content_type="text/plain")
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
