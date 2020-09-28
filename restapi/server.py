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
                            filename='tmp/avn_api.log',
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

@app.route('/start', methods=['PUT'])
def start():
    try:
        threading.Thread(target=Topology.start).start()
        return ("Network start request accepted", 202)
    except Exception as e:
        handle_ex(e)
        return ("Error", 500)

@app.route('/keys', methods=['PUT'])
def keys():
    try:
        threading.Thread(target=Topology.send_keys).start()
        return ("Network keys request accepted", 202)
    except Exception as e:
        handle_ex(e)
        return ("Error", 500)

    
@app.route('/destroy', methods=['DELETE'])
def destroy():
    try:
        threading.Thread(target=Topology.destroy).start()
        return ("Network destroy request accepted", 202)
    except Exception as e:
        handle_ex(e)
        return ("Error", 500)

@app.route('/details/hosts', methods=['GET'])
def host_details():
    try:
        host_data = Topology.show_hosts()
        return (jsonify(host_data), 200)
    except Exception as e:
        handle_ex(e)
        return ("Error", 500)

@app.route('/details/networks', methods=['GET'])
def network_details():
    try:
        network_data = Topology.show_networks()
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



