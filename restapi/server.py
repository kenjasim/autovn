from gevent.pywsgi import WSGIServer
from gevent.pywsgi import LoggingLogAdapter
from flask import Flask, Response
import logging 

from models.topo import Topology

app = Flask(__name__) 
app.debug = False
app.use_reloader = False
topo = Topology() 

logger = logging.getLogger()
log = LoggingLogAdapter(logger, level=10) 

@app.route('/hosts', methods=['GET']) 
def get_hosts():
    topo.get_hosts() 
    s = ''.join([h.vmname for h in topo.get_hosts()]) 
    return "<h1>Hosts: " + s + "</h1>"

def server_start(): 
    http_server = WSGIServer(('', 5000), application=app, log=log, error_log=log) 
    http_server.serve_forever() 



