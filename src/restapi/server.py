from gevent.pywsgi import WSGIServer, LoggingLogAdapter
from flask import Flask, Response, jsonify, request
from flask_jwt import JWT
import multiprocessing, logging, threading
from print_colours import Print
import atexit
import subprocess
from pathlib import Path 
import os
import shutil 
import sys
import functools
from contextlib import redirect_stdout

from security import authorise, authenticate
from resources import Hosts, Networks, SSHForward, Users
from topo import Topology

# Initialise app-rest Api server 
app = Flask(__name__)
app.debug = False
app.use_reloader = False

logger = logging.getLogger()
log = LoggingLogAdapter(logger, level=10)

#authentication decorator
def make_secure():
    def decorator(func):
        @functools.wraps(func)
        def secure_function(*args, **kwargs):
            username = request.headers.get('username')
            token = request.headers.get('token')
            if authorise(username, token):
                return func(*args, **kwargs)
            else:
                return jsonify({'message': "Token authentication failed"}), 401
        return secure_function
    return decorator


def handle_ex(exception):
    """Print exception and traceback."""
    logging.exception(exception)
    Print.print_error(exception)

################################################################################
# Rest API Endpoints
################################################################################
@app.route('/', methods=['GET'])
def check():
    return ("<h1>Server avaliable.</h1>", 200)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    print(data)
    if 'username' in data and 'password' in data:
        try:
            token = authenticate(data['username'], data['password'])
            if token:
                return jsonify([{'token': token}]), 200
            else:
                return jsonify({'message': "Username and password failed to authenticate"}), 401
        except Exception as e:
            handle_ex(e)
            return ("Error", 500) 

@app.route('/build', methods=['PUT'])
@app.route('/build/<string:template>', methods=['PUT'])
def build(template="default.yaml"):
    try:
        threading.Thread(target=Topology.build, args=(template,)).start()
        return ("Network build accepted", 202)
    except Exception as e:
        handle_ex(e)
        return ("Error", 500)

@app.route('/start/<string:deployment_name>', methods=['PUT'])
@make_secure()
def start(deployment_name):
    try:
        threading.Thread(target=Topology.start, args=(deployment_name, )).start()
        return ("Network start request accepted", 202)
    except Exception as e:
        handle_ex(e)
        return ("Error", 500)

@app.route('/stop/<string:deployment_name>', methods=['PUT'])
@make_secure()
def stop(deployment_name):
    try:
        threading.Thread(target=Topology.stop, args=(deployment_name, )).start()
        return ("Network stop request accepted", 202)
    except Exception as e:
        handle_ex(e)
        return ("Error", 500)

@app.route('/restart/<string:deployment_name>', methods=['PUT'])
@make_secure()
def restart(deployment_name):
    try:
        threading.Thread(target=Topology.restart, args=(deployment_name, )).start()
        return ("Network restart request accepted", 202)
    except Exception as e:
        handle_ex(e)
        return ("Error", 500)

@app.route('/keys/<string:deployment_name>', methods=['PUT'])
@make_secure()
def keys(deployment_name):
    try:
        threading.Thread(target=Topology.send_keys, args=(deployment_name, )).start()
        return ("Network keys request accepted", 202)
    except Exception as e:
        handle_ex(e)
        return ("Error", 500)

    
@app.route('/destroy/<string:deployment_name>', methods=['DELETE'])
@make_secure()
def destroy(deployment_name):
    try:
        threading.Thread(target=Topology.destroy, args=(deployment_name, )).start()
        return ("Network destroy request accepted", 202)
    except Exception as e:
        handle_ex(e)
        return ("Error", 500)

@app.route('/details/hosts', methods=['GET'])
@make_secure()
def host_details():
    try:
        host_data = Topology.host_details()
        return (jsonify(host_data), 200)
    except Exception as e:
        handle_ex(e)
        return ("Error", 500)

@app.route('/details/networks', methods=['GET'])
@make_secure()
def network_details():
    try:
        network_data = Topology.network_details()
        return (jsonify(network_data), 200)
    except Exception as e:
        handle_ex(e)
        return ("Error", 500)

@app.route('/hosts', methods=['GET'])
@make_secure()
def get_hosts():
    try:
        hosts = Hosts().get_all()
        return jsonify([host.dict() for host in hosts]), 200
    except Exception as e:
        handle_ex(e)
        return ("Error", 500)

@app.route('/networks', methods=['GET'])
@make_secure()
def get_networks():
    try:
        networks = Networks().get_all()
        return jsonify([network.dict() for network in networks]), 200
    except Exception as e:
        handle_ex(e)
        return ("Error", 500)

@app.route('/host/<string:vmname>/ipv4', methods=['GET'])
@make_secure()
def get_ip(vmname):
    try:
        ip = Hosts().get_ip(vmname)
        return jsonify([{'ip': ip}]), 200
    except Exception as e:
        handle_ex(e)
        return ("Error", 500)

@app.route('/host/<string:vmname>/ssh_port', methods=['GET'])
@make_secure()
def get_ssh_remote_port(vmname):
    try:
        port = Hosts().get_ssh_remote_port(vmname)
        return jsonify([{'port': port}]), 200
    except Exception as e:
        handle_ex(e)
        return ("Error", 500)

@app.route('/sshforward/<string:deployment_name>', methods=['PUT'])
@make_secure()
def ssh_forward(deployment_name):
    try:
        Topology.start_ssh_forwarder(deployment_name)
        return "SSH forwarding server for deployment {0} started".format(deployment_name), 200
    except Exception as e:
        handle_ex(e)
        return ("Error", 500)

@app.route('/stopsshforwarding/<string:deployment_name>', methods=['DELETE'])
@make_secure()
def stop_ssh_forward(deployment_name):
    try:
        Topology.stop_ssh_forwarders(deployment_name)
        return "SSH forwarding servers stopped", 200
    except Exception as e:
        handle_ex(e)
        return ("Error", 500)

# @app.route('/register', methods=['PUT'])
# def register(deployment_name):
#     try:
#         Topology.stop_ssh_forwarders(deployment_name)
#         return "SSH forwarding servers stopped", 200
#     except Exception as e:
#         handle_ex(e)
#         return ("Error", 500)

################################################################################
# Rest API Server Object 
################################################################################

class RESTServer(object):
    """Http WSGI Server to wrap Flask API app server."""

    def __init__(self, remote, address="127.0.0.1", port=5000, rport=6001, verbose=True):
        self.remote = remote
        self.address = address
        self.port = port
        self.rport = rport
        self.verbose = verbose
        self.http_server = None
        # Required for Mac Catalina  
        try:
            multiprocessing.set_start_method("fork")
        except RuntimeError:
            pass
        # Setup nginx server config files 
        self.write_proxy_configs()
        self.set_proxy_configs()

    def start(self):
        """Start Rest API server."""
        atexit.register(self.do_exit)
        self.http_server = WSGIServer((self.address, self.port), application=app, log=log, error_log=log)
        self.proc = multiprocessing.Process(target=self.start_http_server)
        self.proc.start()
        # Start reverse proxy if remote
        if not self.remote:
            Print.print_success("Server avaliable at: http://" + self.address + ":" + str(self.port) + "/")
        else: 
            self.start_proxy() 
            Print.print_success("Server avaliable at: https://" + "<public-ip>" + ":" + str(self.rport) + "/")

    def start_http_server(self):
        """Start rest api server, to be called within multiprocess.Process"""
        if not self.verbose:
            homedir = Path().home()
            # Initialise logging handling 
            logger = logging.getLogger()
            sys.stdout.write = logger.info
        self.http_server.serve_forever()  
    
    def write_proxy_configs(self):
        """Create proxy configs files for nginx reverse proxy server"""
        # Make reverse proxy config files 
        proxy_path_src = Path(__file__).parent.absolute() / "proxy"
        proxy_path_dst = Path().home() / ".avn" / "proxy"
        if not os.path.isfile(str(proxy_path_dst / "nginx.conf")):
            shutil.copy(str(proxy_path_src / "nginx.conf"), str(proxy_path_dst / "nginx.conf"))
        if not os.path.isfile(str(proxy_path_dst / "mime.types")):    
            shutil.copy(str(proxy_path_src / "mime.types"), str(proxy_path_dst / "mime.types"))
    
    def set_proxy_configs(self):
        """Update nginx server configuration file's bind port"""
        home_path = Path().home()
        proxy_config_path = Path().home() / ".avn" / "proxy" / "nginx.conf"
        nl = []
        with open(str(proxy_config_path), 'r') as f:
            lines = list(f)
            for line in lines: 
                if "listen" in line: 
                    nl.append("       listen       " + str(self.rport) + " ssl;\n")
                elif "$HOME" in line: 
                    nl.append(line.replace("$HOME", str(home_path)))
                else: 
                    nl.append(line)  
        with open(str(proxy_config_path), 'r+') as f:
            f.writelines(nl) 

    def start_proxy(self):
        """Start nginx reverse proxy server for external access."""
        # Generate certificates if non-exist 
        cert_path = Path().home() / ".avn" / "certs" / "cert.pem"
        cert_key_path = Path().home() / ".avn" / "certs" / "cert.key"
        if not (os.path.isfile(str(cert_path)) and os.path.isfile(str(cert_key_path))):
            cmd = "openssl req -x509 -nodes -days 365 -newkey rsa:2048"
            cmd += " -keyout {0} ".format(cert_key_path)
            cmd += " -out {0}".format(cert_path)
            # Subject fields 
            cmd += " -subj "
            subjects = ["/C=UK", "/ST=London", "/L=London", "/O=AVN", "/CN=autovirtualnetwork"]
            for subject in subjects:
                cmd += subject
            # Create certificates in .avn/certs config dir 
            subprocess.getoutput(cmd)
        # Starting nginx server
        server_config_path = Path().home() / ".avn" / "proxy" / "nginx.conf"
        cmd = "nginx -c {0}".format(server_config_path)
        subprocess.getoutput(cmd)
        
    def stop(self):
        """Strop Rest API server"""
        self.http_server.stop()
        self.http_server.close()
        self.proc.terminate()
        # Stop nginx reverse proxy server
        cmd = "nginx -s stop"
        subprocess.getoutput(cmd)

    def do_exit(self):
        """Handle exit, and cleanup SSH forwarding servers for Rest API only mode"""
        for server in SSHForward.get_all():
            SSHForward.delete(server)

################################################################################
# Resources 
################################################################################

# https://github.com/pytest-dev/pytest-flask/issues/104