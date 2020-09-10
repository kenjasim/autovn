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

class Console(Cmd):
    prompt = ">>> "

    def __init__(self):
        Cmd.__init__(self)
        self.topo = None
        # Create topology 
        print("Initialising network...")
        self.do_build("")
        print("Initialisation complete.")
        print("Starting virtual machines...")
        self.do_start("")
        print("Network is live.")

    ############################################
    # Build Network Topology 
    ############################################

    def do_build(self, cmd):
        """
        Initialise network. 
        """
        try:
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
            print("[!] Invalid number of arguments, see 'help show'")
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
        """
        try:
            self.topo.shells() 
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
            self.topo.send_keys() 
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
        return True

################################################################################
# CLI Exception handler 
################################################################################

def handle_ex(exception):
    """Print exception and traceback."""
    print("[!] Exception Error")
    print(exception)
    track = traceback.format_exc()
    print(track)

################################################################################
# Main
################################################################################

if __name__ == '__main__':
    console = Console().cmdloop()