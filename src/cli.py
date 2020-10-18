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

from resources import Hosts, SSHForward, Users

class Console(Cmd):
    """Command Line Interface for the Automated Virtual Network (AVN) application."""
    # Command-line intro and prompt settings 
    prompt = ">>> "
    intro_file = str(Path(__file__).parent.absolute() / "misc" / "intro.txt" )
    with open(intro_file, 'r') as f:
        intro = f.read()

    def __init__(self, remote=False, url="http://127.0.0.1:5000/"):
        """
        Initialise and run command-line interface.
        Options:
            remote (bool): connect to remote AVN server, default false 
            url     (str): url of remote AVN server
        """
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

        #Exit cleanup on keyboard interrupt
        atexit.register(self.do_exit, "")

    ############################################
    # Login
    ############################################

    def do_login(self, cmd):
        """
        Login to remote rest api (remote only).
        Usage:
            login <username> <password>
        """
        cmds = cmd.split()
        if len(cmds) != 2:
            Print.print_warning("Invalid number of arguments, see 'help login'")
            return

        try:
            Print.print_information("Logging in...")
            if not self.remote:
                Print.print_information("Non remote client doesnt need authentication")
                return
            self.client.login(cmds[0], cmds[1])
        except Exception as e:
            handle_ex(e)

    ############################################
    # Build Network Topology
    ############################################

    def do_build(self, cmd):
        """
        Initialise network. Leave template blank for default 3h-1n config.
        Usage:
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
        Usage:
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
        Usage:
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
        Usage:
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
        Usage:
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
            if cmds[0] == 'u':
                print(create_table(Users.get_all()))
        except Exception as e:
            handle_ex(e)

    ############################################
    # Open Shell with a host 
    ############################################

    def do_shell(self, cmd):
        """
        Start shell session with vm.
        Usage:
            shell <vmname> (if hosted locally)
            shell <vmname> <server_ip> <username> <password> (if hosted remotely)
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
        Usage:
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
    # Start SSH Forwarding
    ############################################
    
    def do_sshforward(self, cmd):
        """
        Startup SSH forwarders for remote host ssh connection
        Usage:
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
    # Stop SSH Forwarding 
    ############################################

    def do_stopsshforward(self, cmd):
        """
        Stop the ssh forwarding server per deployment 
        Usage:
            stopsshforward <deployment-name>
        """
        # command validation
        cmds = cmd.split()
        if len(cmds) != 1:
            Print.print_warning("Invalid number of arguments, see 'help stopsshforwarding'")
            return

        # command execution 
        try:
            Print.print_information("Killing ssh forwarding processes...")
            # if self.server:
            #     self.server.stop()
            self.client.stop_ssh_forwarders(cmds[0])
        except Exception as e:
            handle_ex(e)

    ############################################
    # Launch RestAPI Server
    ############################################

    def do_server(self, cmd):
        """
        Launch the RestAPI Server.
        Usage:
            server
            server r (Opens RestAPI Server to public network with SSL encryption, https)
        """
        # command validation
        cmds = cmd.split()
        remote = False
        if len(cmds) == 0:
            Print.print_information("Starting rest API on localhost only (http)")
        elif len(cmds) == 1 and cmds[0] == 'r':
            remote = True
            Print.print_information("Starting rest API, publicly accesible (https)")
        else: 
            Print.print_warning("Invalid number of arguments, see 'help stopsshforwarding'")
            return
        # command execution 
        try:
            Print.print_information("Starting RestAPI server...")
            if self.remote:
                 Print.print_warning("Running as remote client, RestAPI server not applicable.")
            self.server = RESTServer(remote, verbose=False)
            self.server.start()
        except Exception as e:
            handle_ex(e)

    ############################################
    # Register rest API user
    ############################################

    def do_register(self, cmd):
        """
        Register a user to the Rest API

        Usage:
            register <username>
        """
        # command validation
        cmds = cmd.split()
        if len(cmds) != 1:
            Print.print_warning("Invalid number of arguments, see 'help register'")
            return
        # command execution
        try:
            if self.remote:
                Print.print_warning("Cannot create account using remote registeration")
                return
            password = input("Enter Password: ")
            password_check = input ("Re-enter Password: ")
            if password == password_check:
                Print.print_information("Passwords match, creating account")
                Users.post(cmds[0], password)
            else:
                Print.print_warning("Passwords dont match")
        except Exception as e:
            handle_ex(e)

    ############################################
    # Remove rest API user
    ############################################

    def do_remove(self, cmd):
        """
        Remove a user from the Rest API

        Usage:
            remove <username>
        """
        # command validation
        cmds = cmd.split()
        if len(cmds) != 1:
            Print.print_warning("Invalid number of arguments, see 'help register'")
            return
        # command execution
        try:
            if self.remote:
                Print.print_warning("Cannot create account using remote registeration")
                return

            # Remove user
            Users.remove_user(cmds[0])
        except Exception as e:
            handle_ex(e)
    
    ############################################
    # Network Destroy
    ############################################

    def do_destroy(self, cmd):
        """
        Destroy the vms and network interfaces within a deployment.
        Usage:
            destroy <deployment-name>
        """
        # command validation
        cmds = cmd.split()
        if len(cmds) != 1:
            Print.print_warning("Invalid number of arguments, see 'help destroy'")
            return

        try:
            Print.print_information("Destroying network...")
            self.client.destroy(cmds[0])
        except Exception as e:
            handle_ex(e)
            print("Destroy failed, mannual Deployment cleanup require:")
            print("1. Remove virtual machines from virtual box via cli")
            print("2. Remove host-only network from virtual box via cli")
            print("3. Delete DHCP leases from:")
            print("\t ~/.config/VirtualBox/ (Linux)")
            print("\t ~/Library/VirtualBox (Mac)")    
            print("4. Remove SSH keys for hosts from ~/.ssh/known_hosts")

    ############################################
    # exit process
    ############################################

    def do_exit(self, cmd):
        """
        Exit the application.
        Usage:
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

################################################################################
# Formatting
################################################################################

def create_table(items):
    """
    Create and print a table to the console from a dict.
    Options:
        items (dict): {dict of items:}
    Returns
        output (str): formatted string
    """
    header = items[0].keys()
    rows =  [item.values() for item in items]
    return tabulate(rows, header,tablefmt="fancy_grid")

################################################################################
# Main
################################################################################

if __name__ == '__main__':
    console = Console().cmdloop()
