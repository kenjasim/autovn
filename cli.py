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
from print_colours import Print
import logging

class Console(Cmd):
    prompt = ">>> "
    with open('misc/intro.txt', 'r') as f:
        intro = f.read()

    def __init__(self):
        Cmd.__init__(self)
        self.topo = None
        logging.basicConfig(level=logging.DEBUG,
                            filename='avn.log',
                            format='%(asctime)s, %(levelname)s, %(name)s, %(message)s')

    ############################################
    # Build Network Topology
    ############################################

    def do_build(self, cmd):
        """
        Initialise network. Leave template blank for default k8 configuration

        build <template>
        """
        cmds = cmd.split()
        if len(cmds) > 1:
            Print.print_warning("Invalid number of arguments, see 'help build'")
            return

        try:
            Print.print_information("Initialising network...")
            if len(cmds) == 1:
                self.topo = Topology(template_file=cmds[0])
            else:
                self.topo = Topology()
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
            self.topo.start()
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
                self.topo.show_hosts()
            if cmds[0] == 'n':
                self.topo.show_networks()
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
            self.topo.shell(vmname)
        except Exception as e:
            handle_ex(e)

    ############################################
    # Distribute Keys
    ############################################

    def do_keys(self, cmd):
        """
        Distribute SSH keys to hosts.
        """
        try:
            Print.print_information("Distributing keys...")
            self.topo.send_keys()
        except Exception as e:
            handle_ex(e)

    ############################################int.print_information
    # Network Destroy
    ############################################

    def do_destroy(self, cmd):
        """
        Destroy the network.
        """
        try:
            Print.print_information("Destroying network...")
            self.topo.destroy()
        except Exception as e:
            handle_ex(e)

    ############################################
    # exit process
    ############################################

    def do_exit(self, cmd):
        """
        exit the application
        """
        # Destroy network
        a = input("Destroy the network before exiting application (y/n):")
        if a == 'y':
            self.do_destroy("")
        return True

################################################################################
# CLI Exception handler
################################################################################

def handle_ex(exception):
    """Print exception and traceback."""
    logging.exception(exception)
    Print.print_error(exception)

################################################################################
# Main
################################################################################

if __name__ == '__main__':
    console = Console().cmdloop()
