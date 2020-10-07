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

    def __init__(self):
        Cmd.__init__(self)
        self.server = None
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
                Topology.build(template_file=cmds[0])
            else:
                Topology.build()
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
            Print.print_warning("Invalid number of arguments, see 'help show'")
            return
        try:
            Print.print_information("Starting network...")
            Topology.start(cmds[0])
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
            Print.print_warning("Invalid number of arguments, see 'help show'")
            return
        try:
            Print.print_information("Restarting virtual machines...")
            Topology.restart(cmds[0])
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
                print(create_table(Topology.show_hosts()))
            if cmds[0] == 'n':
                print(create_table(Topology.show_networks()))
        except Exception as e:
            handle_ex(e)

    ############################################
    # Open Shells
    ############################################

    def do_shell(self, cmd):
        """
        Start shell session with vm.

        shell <vmname>
        """
        # command validation
        cmds = cmd.split()
        if len(cmds) != 1:
            Print.print_warning("Invalid number of arguments, see 'help show'")
            return
        
        # command execution
        Print.print_information("Establishing shell...")
        try:
            Topology.shell(cmds[0])
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
            Topology.send_keys(cmds[0])
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
            Print.print_warning("Invalid number of arguments, see 'help keys'")
            return

        try:
            Print.print_information("Destroying network...")
            # if self.server:
            #     self.server.stop()
            Topology.destroy(cmds[0])
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
