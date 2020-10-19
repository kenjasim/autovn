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
from template import Template
from getpass import getpass
from security import change_password, remove_user

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
            login <username>
        """
        cmds = cmd.split()
        if len(cmds) != 1:
            Print.print_warning("Invalid number of arguments, see 'help login'")
            return

        try:
            if not self.remote:
                Print.print_information("Non remote client doesnt need authentication")
                return

            Print.print_information("Logging in...")
            password = getpass("Enter Password: ")
            self.client.login(cmds[0], password)
        except Exception as e:
            handle_ex(e)

    ############################################
    # password
    ############################################

    def do_passwd(self, cmd):
        """
        Change username for REST API user.
        Usage:
            passwd <username>
        """
        cmds = cmd.split()
        if len(cmds) != 1:
            Print.print_warning("Invalid number of arguments, see 'help passwd'")
            return

        try:
            Print.print_information("Changing user password...")
            # Enter in the passwords
            curr_password = getpass("Enter old Password: ")
            password = getpass("Enter new Password: ")
            password_check = getpass("Re-Enter new Password: ")
            if password != password_check:
                Print.print_warning("Passwords dont match")
                return
            elif self.remote:
                self.client.change_password(cmds[0], curr_password, password)
            else:
                change_password(cmds[0], curr_password, password)
                    
        except Exception as e:
            handle_ex(e)

    ############################################
    # Remove user
    ############################################

    def do_remove(self, cmd):
        """
        Remove rest api user.
        Usage:
            remove <username>
        """
        cmds = cmd.split()
        if len(cmds) != 1:
            Print.print_warning("Invalid number of arguments, see 'help passwd'")
            return

        try:
            Print.print_information("Removing user...")
            # Enter in the passwords
            password = getpass("Enter Password: ")
            password_check = getpass("Re-Enter Password: ")
            
            if password != password_check:
                Print.print_warning("Passwords dont match")
                return
            elif self.remote:
                self.client.remove_user(cmds[0], password)
            else:
                remove_user(cmds[0], password)
                    
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
                print(create_table(self.client.host_details(), header=["vmname", "VMState", "ostype", "cpus", "memory", "deployment"]))
            if cmds[0] == 'n':
                print(create_table(self.client.network_details(), header=["vmname", "name", "netname", "mac", "ip", "deployment"]))
            if cmds[0] == 'u':
                if self.remote:
                    Print.print_warning("Can't see users as remote client")
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
            sshforward [option] <deployment-name> 
            Options:
                start:  starts ssh forwarding server(s)
                stop:   stops ssh forwarding server(s)
        """
        # command validation
        cmds = cmd.split()
        if len(cmds) != 2:
            Print.print_warning("Invalid number of arguments, see 'help sshforward'")
            return

        # command execution
        try:
            if cmds[0] == "start":
                Print.print_information("Starting SSH forwarder server...")
                self.client.start_ssh_forwarder(cmds[1])
            elif cmds[0] == "stop":
                Print.print_information("Killing ssh forwarding processes...")
                self.client.stop_ssh_forwarders(cmds[1])
            else:
                Print.print_warning("Invalid option, see 'help sshforward'")
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
        except Exception as e:
            handle_ex(e)
            return
        try:
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
            # Enter a password for the user
            password = getpass("Enter Password: ")
            password_check = getpass("Re-Enter Password: ")
            if password != password_check:
                Print.print_warning("Passwords dont match")
            elif self.remote:
                Print.print_information("Passwords match, creating account")
                self.client.register(cmds[0], password)
            else:
                Print.print_information("Passwords match, creating account")
                Users.post(cmds[0], password)
        except Exception as e:
            handle_ex(e)
    
    ############################################
    # Create template 
    ############################################

    def do_create(self, cmd):
        """
        Add a topology template to the application config folder.

        Usage:
            create -f <path/to/template.yaml>
            create -g <github/url> 
        """
        # command validation
        cmds = cmd.split()
        if len(cmds) != 2:
            Print.print_warning("Invalid number of arguments, see 'help create'")
            return
        # command execution
        try:
            temp = Template() 
            # Main Cli (template > config-dir)
            if cmds[0] == '-f' and not self.remote:
                temp.copy_template(cmds[1]) 
            # Remote Cli (template > client > json > server > yaml > config-dir)
            elif cmds[0] == '-f' and self.remote:
                temp.send_template(cmds[1]) 
            # Git pull (git > config-dir)
            elif cmds[0] == '-g':
                temp.pull_template(cmds[1], self.remote) 
            else: 
                raise Exception("Invalid options, see 'help create'")

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

def create_table(items, header = []):
    """
    Create and print a table to the console from a dict.
    Options:
        items (dict): {dict of items:}
    Returns
        output (str): formatted string
    """
    if header == []:
        header = items[0].keys()
    else:
        items = [{val: item[val] for val in header} for item in items]
    
    rows =  [item.values() for item in items]
    return tabulate(rows, header,tablefmt="fancy_grid")

################################################################################
# Main
################################################################################

if __name__ == '__main__':
    console = Console().cmdloop()
