from gevent.pywsgi import WSGIServer, LoggingLogAdapter
from flask import Flask, Response, jsonify
import multiprocessing, logging

from resources import Hosts, Networks

app = Flask(__name__)
app.debug = False
app.use_reloader = False

logger = logging.getLogger()
log = LoggingLogAdapter(logger, level=10)

@app.route('/hosts', methods=['GET'])
def get_hosts():
    hosts = Hosts().get_all()
    return jsonify([host.dict() for host in hosts])

@app.route('/networks', methods=['GET'])
def get_networks():
    networks = Networks().get_all()
    return jsonify([network.dict() for network in networks])

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

    def stop(self):
        self.http_server.stop()
        self.http_server.close()
        self.proc.terminate()
