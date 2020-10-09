from gevent.pywsgi import WSGIServer, LoggingLogAdapter
from flask import Flask, Response, jsonify
import multiprocessing, logging, threading
from print_colours import Print

from resources import Hosts, Networks
from topo import Topology

app = Flask(__name__)
app.debug = False
app.use_reloader = False

logging.basicConfig(level=logging.DEBUG,
                            filename='tmp/avn.log',
                            format='%(asctime)s, %(levelname)s, %(name)s, %(message)s')

logger = logging.getLogger()
log = LoggingLogAdapter(logger, level=10)

def handle_ex(exception):
    """Print exception and traceback."""
    logging.exception(exception)
    Print.print_error(exception)

#####################
# Topology Commands #
#####################

@app.route('/build', methods=['PUT'])
@app.route('/build/<string:template>', methods=['PUT'])
def build(template="default.yaml"):
    try:
        threading.Thread(target=Topology.build, args=(template,)).start()
        return ("Network build accepted", 202)
    except Exception as e:
        handle_ex(e)
        return ("Error", 500)

@app.route('/', methods=['GET'])
def check():
    return ("<h1>Server avaliable.</h1>", 200)

@app.route('/start/<string:deployment_name>', methods=['PUT'])
def start(deployment_name):
    try:
        threading.Thread(target=Topology.start, args=(deployment_name, )).start()
        return ("Network start request accepted", 202)
    except Exception as e:
        handle_ex(e)
        return ("Error", 500)

@app.route('/stop/<string:deployment_name>', methods=['PUT'])
def stop(deployment_name):
    try:
        threading.Thread(target=Topology.stop, args=(deployment_name, )).start()
        return ("Network stop request accepted", 202)
    except Exception as e:
        handle_ex(e)
        return ("Error", 500)

@app.route('/restart/<string:deployment_name>', methods=['PUT'])
def restart(deployment_name):
    try:
        threading.Thread(target=Topology.restart, args=(deployment_name, )).start()
        return ("Network restart request accepted", 202)
    except Exception as e:
        handle_ex(e)
        return ("Error", 500)

@app.route('/keys/<string:deployment_name>', methods=['PUT'])
def keys(deployment_name):
    try:
        threading.Thread(target=Topology.send_keys, args=(deployment_name, )).start()
        return ("Network keys request accepted", 202)
    except Exception as e:
        handle_ex(e)
        return ("Error", 500)

    
@app.route('/destroy/<string:deployment_name>', methods=['DELETE'])
def destroy(deployment_name):
    try:
        threading.Thread(target=Topology.destroy, args=(deployment_name, )).start()
        return ("Network destroy request accepted", 202)
    except Exception as e:
        handle_ex(e)
        return ("Error", 500)

@app.route('/details/hosts', methods=['GET'])
def host_details():
    try:
        host_data = Topology.host_details()
        return (jsonify(host_data), 200)
    except Exception as e:
        handle_ex(e)
        return ("Error", 500)

@app.route('/details/networks', methods=['GET'])
def network_details():
    try:
        network_data = Topology.network_details()
        return (jsonify(network_data), 200)
    except Exception as e:
        handle_ex(e)
        return ("Error", 500)

@app.route('/hosts', methods=['GET'])
def get_hosts():
    try:
        hosts = Hosts().get_all()
        return jsonify([host.dict() for host in hosts]), 200
    except Exception as e:
        handle_ex(e)
        return ("Error", 500)

@app.route('/networks', methods=['GET'])
def get_networks():
    try:
        networks = Networks().get_all()
        return jsonify([network.dict() for network in networks]), 200
    except Exception as e:
        handle_ex(e)
        return ("Error", 500)

@app.route('/host/<string:vmname>/ipv4', methods=['GET'])
def get_ip(vmname):
    try:
        ip = Hosts().get_ip(vmname)
        return jsonify([{'ip': ip}]), 200
    except Exception as e:
        handle_ex(e)
        return ("Error", 500)

@app.route('/host/<string:vmname>/ssh_port', methods=['GET'])
def get_ssh_remote_port(vmname):
    try:
        port = Hosts().get_ssh_remote_port(vmname)
        return jsonify([{'port': port}]), 200
    except Exception as e:
        handle_ex(e)
        return ("Error", 500)

@app.route('/sshforward/<string:deployment_name>', methods=['PUT'])
def ssh_forward(deployment_name):
    try:
        Topology.start_ssh_forwarder(deployment_name)
        return "SSH forwarding server for deployment {0} started".format(deployment_name), 200
    except Exception as e:
        handle_ex(e)
        return ("Error", 500)


class RESTServer(object):

    def __init__(self, address="", port=5000):
        self.address = address
        self.port = port
        self.http_server = None
        # https://github.com/pytest-dev/pytest-flask/issues/104
        multiprocessing.set_start_method("fork")

    def start(self):
        self.http_server = WSGIServer((self.address, self.port), application=app, log=log, error_log=log)
        self.proc = multiprocessing.Process(target=self.http_server.serve_forever)
        self.proc.start()
        if self.address == "": 
            self.address = "127.0.0.1"
        Print.print_success("Server avaliable at: http://" + self.address + ":" + str(self.port) + "/")

    def stop(self):
        self.http_server.stop()
        self.http_server.close()
        self.proc.terminate()



