from gevent.pywsgi import WSGIServer
from gevent.pywsgi import LoggingLogAdapter
from flask import Flask, Response
import multiprocessing
import logging

from resources import Hosts

app = Flask(__name__)
app.debug = False
app.use_reloader = False

logger = logging.getLogger()
log = LoggingLogAdapter(logger, level=10)

@app.route('/hosts', methods=['GET'])
def get_hosts():
    return Hosts().get_all()

class RESTServer(object):

    def __init__(self, address="", port=5000):
        self.address = address
        self.port = port
        self.http_server = None

    def start(self):
        self.http_server = WSGIServer((self.address, self.port), application=app, log=log, error_log=log)
        self.proc = multiprocessing.Process(target=self.http_server.serve_forever)
        self.proc.start()

    def stop(self):
        self.http_server.stop()
        self.http_server.close()
        self.proc.terminate()
