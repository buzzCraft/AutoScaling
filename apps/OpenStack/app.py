
from flask import Flask, jsonify
from openstack_check import get_running_servers

app = Flask(__name__)

@app.route('/metrics', methods=['GET'])
def metrics():
    running_servers = get_running_servers()
    return jsonify({'running_servers': running_servers})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)