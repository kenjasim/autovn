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

from resources import Hosts

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

        build <path-to-template>
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
        Initialise network.
        """
        try:
            Print.print_information("Starting network...")
            self.client.start()
        except Exception as e:
            handle_ex(e)
    
    ############################################
    # Restart Virtual Machines
    ############################################

    def do_restart(self, cmd):
        """
        Restart the virtual machines.
        """
        try:
            Print.print_information("Restarting virtual machines...")
            self.client.restart()
        except Exception as e:
            handle_ex(e)

    ############################################
    # Show properties
    ############################################

    def do_show(self, cmd):
        """
        Show Topology properties.
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
    # Open Shells
    ############################################

    def do_shell(self, cmd):
        """
        Start shell sessions.
        Options:
            vmname: start a shell session with a specific vm,
            if none specified then sessions started with all.
        """
        # command validation
        Print.print_information("Establishing shell...")
        cmds = cmd.split()
        vmname = "all"
        if len(cmds) == 1:
            vmname = cmds[0]
        # command executionint.print_information
        try:
            self.client.shell(vmname)
        except Exception as e:
            handle_ex(e)

    ############################################
    # Distribute Keys
    ############################################
    
    def do_keys(self, cmd):
        """
        Distribute SSH keys to hosts.

        keys <hostname> 
        keys
        """
        # command validation
        cmds = cmd.split()
        vmname = "all"
        if len(cmds) == 1:
            vmname = cmds[0]
        # command execution
        try:
            Print.print_information("Distributing keys...")
            self.client.send_keys(vmname)
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
        Destroy the network.
        """
        try:
            Print.print_information("Destroying network...")
            # if self.server:
            #     self.server.stop()
            self.client.destroy()
        except Exception as e:
            handle_ex(e)

    ############################################
    # exit process
    ############################################

    def do_exit(self, cmd):
        """
        Exit the application
        """
        try:
            # Stop the rest api if running
            if self.server:
                self.server.stop()

            # Check if there are any hosts, if not then exit without asking to destroy
            Hosts().get_all()

            # Destroy network
            a = input("Destroy the network before exiting (y/n):")
            if a == 'y':
                self.do_destroy("")
            
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
