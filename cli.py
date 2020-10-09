#!/usr/bin/python3

# AutoVBox Command Line
#
# Author: Daniel Crouch
# Date created: September 2020

import os
import re
import time
import traceback
from cmd import Cmd
from topo import Topology
from restapi.client import RESTClient
import atexit
from print_colours import Print
import logging
from restapi.server import RESTServer
import multiprocessing
from pathlib import Path
from tabulate import tabulate
import threading

from resources import Hosts, SSHForward

# Log path 
p = Path().parent.absolute() / "tmp"
if not os.path.isdir(str(p)): 
    os.mkdir(str(p)) 

class Console(Cmd):
    prompt = ">>> "
    with open('misc/intro.txt', 'r') as f:
        intro = f.read()

    def __init__(self, remote=False, url="http://127.0.0.1:5000/"):
        Cmd.__init__(self)
        self.server = None
        self.remote = remote
        self.event = threading.Event()
        if remote:
            self.client = RESTClient
            self.client.set_server_url(url) 
            if self.client.check_link():
                Print.print_success("AVN Server is avaliable.") 
        else:
            self.client = Topology        
        logging.basicConfig(level=logging.DEBUG,
                            filename='tmp/avn.log',
                            format='%(asctime)s, %(levelname)s, %(name)s, %(message)s')

        #Exit cleanup on keyboard interrupt
        atexit.register(self.do_exit, "")

    ############################################
    # Build Network Topology
    ############################################

    def do_build(self, cmd):
        """
        Initialise network. Leave template blank for default 3h-1n config.

        build <path/to/template>
        """
        cmds = cmd.split()
        if len(cmds) > 1:
            Print.print_warning("Invalid number of arguments, see 'help build'")
            return

        try:
            Print.print_information("Initialising topology...")
            if len(cmds) == 1:
                self.client.build(template_file=cmds[0])
            else:
                self.client.build()
        except Exception as e:
            handle_ex(e)

    ############################################
    # Start Network Topology
    ############################################

    def do_start(self, cmd):
        """
        Start virtual machines within a deployment.

        start <deployment-name>    
        """
        # command validation
        cmds = cmd.split()
        if len(cmds) != 1:
            Print.print_warning("Invalid number of arguments, see 'help start'")
            return
        try:
            Print.print_information("Starting network...")
            self.client.start(cmds[0])
        except Exception as e:
            handle_ex(e)
    
    ############################################
    # Restart Virtual Machines
    ############################################

    def do_restart(self, cmd):
        """
        Restart the virtual machines within a deployment.

        restart <deployment-name>  
        """
        cmds = cmd.split()
        if len(cmds) != 1:
            Print.print_warning("Invalid number of arguments, see 'help restart'")
            return
        try:
            Print.print_information("Restarting virtual machines...")
            self.client.restart(cmds[0])
        except Exception as e:
            handle_ex(e)

    ############################################
    # Stop Virtual Machines
    ############################################

    def do_stop(self, cmd):
        """
        Stop the virtual machines within a deployment.

        stop <deployment-name>  
        """
        cmds = cmd.split()
        if len(cmds) != 1:
            Print.print_warning("Invalid number of arguments, see 'help stop'")
            return
        try:
            Print.print_information("Stopping virtual machines...")
            self.client.stop(cmds[0])
        except Exception as e:
            handle_ex(e)

    ############################################
    # Show properties
    ############################################

    def do_show(self, cmd):
        """
        Show properties for all deployments.

        show [option]
        Options:
            h: host properties
            n: network adapter properties
        """
        # command validation
        cmds = cmd.split()
        if len(cmds) != 1:
            Print.print_warning("Invalid number of arguments, see 'help show'")
            return
        # command execution
        try:
            if cmds[0] == 'h':
                print(create_table(self.client.host_details()))
            if cmds[0] == 'n':
                print(create_table(self.client.network_details()))
        except Exception as e:
            handle_ex(e)

    ############################################
    # Open Shell with a host 
    ############################################

    def do_shell(self, cmd):
        """
        Start shell session with vm.

        If local run: shell <vmname>
        If running AVNserver in a remote location then: shell <vmname> <server_ip> <username> <password> 
        """
        # command validation
        cmds = cmd.split()
        options = []
        if self.remote:
            if len(cmds) != 4:
                Print.print_warning("Invalid number of arguments, see 'help shell'")
                return
            options = cmds[0:4]
        else:
            if len(cmds) != 1:
                Print.print_warning("Invalid number of arguments, see 'help shell'")
                return
            options = cmds[0]
        
        # command execution
        Print.print_information("Establishing shell...")
        try:
            self.client.shell(options)
        except Exception as e:
            handle_ex(e)
    

    ############################################
    # Distribute Keys
    ############################################
    
    def do_keys(self, cmd):
        """
        Distribute SSH keys to all hosts within a deployment.

        keys <deployment-name> 
        """
        # command validation
        cmds = cmd.split()
        if len(cmds) != 1:
            Print.print_warning("Invalid number of arguments, see 'help keys'")
            return

        # command execution
        try:
            Print.print_information("Distributing keys...")
            self.client.send_keys(cmds[0])
        except Exception as e:
            handle_ex(e)

    ############################################
    # SSH Forwarder 
    ############################################
    
    def do_sshforward(self, cmd):
        """
        Startup SSH forwarders for remote host ssh connection

        keys <deployment-name> 
        """
        # command validation
        cmds = cmd.split()
        if len(cmds) != 1:
            Print.print_warning("Invalid number of arguments, see 'help sshforward'")
            return

        # command execution
        try:
            Print.print_information("Starting SSH forwarder server...")
            self.client.start_ssh_forwarder(cmds[0])
        except Exception as e:
            handle_ex(e)

    ############################################
    # Launch RestAPI Server
    ############################################

    def do_server(self, cmd):
        """
        Launch the RestAPI Server.
        """
        try:
            if self.remote:
                 Print.print_warning("Running as remote client, RestAPI server not applicable.")
                 return
            Print.print_information("Starting RestAPI server...")
            self.server = RESTServer()
            self.server.start()
        except Exception as e:
            handle_ex(e)

    ############################################
    # Network Destroy
    ############################################

    def do_destroy(self, cmd):
        """
        Destroy the vms and network interfaces within a deployment.

        destroy <deployment-name>
        """
        # command validation
        cmds = cmd.split()
        if len(cmds) != 1:
            Print.print_warning("Invalid number of arguments, see 'help destroy'")
            return

        try:
            Print.print_information("Destroying network...")
            # if self.server:
            #     self.server.stop()
            self.client.destroy(cmds[0])
        except Exception as e:
            handle_ex(e)

    def do_stopsshforwarding(self, cmd):
        """
        Stop the ssh forwarding server per deployment 

        Usage
        stopsshforwarding <deployment-name>
        """
        # command validation
        cmds = cmd.split()
        if len(cmds) != 1:
            Print.print_warning("Invalid number of arguments, see 'help stopsshforwarding'")
            return

        try:
            Print.print_information("Killing ssh forwarding processes...")
            # if self.server:
            #     self.server.stop()
            self.client.stop_ssh_forwarders(cmds[0])
        except Exception as e:
            handle_ex(e)
        



    ############################################
    # exit process
    ############################################

    def do_exit(self, cmd):
        """
        Exit the application

        exit
        """
        try:
            # Stop the rest api if running
            if self.server:
                self.server.stop()

            #If running local client then ensure the records are cleared
            if not self.remote:
                for server in SSHForward.get_all():
                    SSHForward.delete(server)
            
        except Exception as e:
            handle_ex(e)
        finally:
            return True


################################################################################
# CLI Exception handler
################################################################################

def handle_ex(exception):
    """Print exception and traceback."""
    logging.exception(exception)
    Print.print_error(exception)

def create_table(items):
    """
    Create and print a table to the console
    from a dict

    Keyword Arguments:
        items - a dict of items

    Returns
        nicely formatted table string
    """
    header = items[0].keys()
    rows =  [item.values() for item in items]
    return tabulate(rows, header,tablefmt="fancy_grid")

################################################################################
# Main
################################################################################

if __name__ == '__main__':
    console = Console().cmdloop()
