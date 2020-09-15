from gevent.pywsgi import WSGIServer
from gevent.pywsgi import LoggingLogAdapter
from flask import Flask, Response
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

def server_start():
    http_server = WSGIServer(('', 5000), application=app, log=log, error_log=log)
    http_server.serve_forever()
