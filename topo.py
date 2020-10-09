import os,sys
from concurrent.futures import ThreadPoolExecutor
import time
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
from tabulate import tabulate
import traceback

from models.network import Network
from models.host import Host
from models.deployment import Deployment
from models.port_forward import PortForward
from resources import Hosts, Networks, Deployments, SSHForward
from constructor import Constructor
from print_colours import Print

from db import Session, create_tables, close_database, return_tables

class Topology():
    """Collection of methods to build/interact with a deployment topology."""

    @staticmethod
    def build(template_file="default.yaml"):
        """
        Read a yaml configuration file to get the network required and then
        initialise the network
        """
        # Make sure that the tables are created
        create_tables()

        # Check if the file exits, if not then raise an exception
        Constructor(template_file).parse()
    
    @staticmethod
    def start(deployment_name):
        """Start virtual network and machines."""
        # Get the hosts from the database
        hosts = Hosts().get_deployment_by_name(deployment_name)
        if hosts:
            # Start the thread executor
            executor = ThreadPoolExecutor(max_workers=len(hosts))
            threads = []

            # Assign each host start command to a thread
            for host in hosts:
                t = executor.submit(host.start)
                threads.append(t)
            # Wait for all threaded processes to complete
            for thread in threads:
                thread.result()
            # Poll hosts for IP assignment
            Topology.poll_ips(deployment_name)
        else:
            Print.print_error("No Deployment with name {name}".format(name=deployment_name))

    @staticmethod
    def poll_ips(deployment_name, timeout=30):
        """
        Poll hosts for IP assignment.
        Options: 
            deployment_name (str): name of the deployment 
            timeout         (int): polling timeout in seconds, default is 30s
        """
        # Get the hosts from the database
        hosts = Hosts().get_deployment_by_name(deployment_name)
        # Poll all hosts until response received from each
        if hosts:
            t = time.time()
            while time.time() - t < timeout and len(hosts) > 0:
                time.sleep(1)
                for host in hosts:
                    if host.get_ip():
                        hosts.remove(host)
            if len(hosts) > 0:
                Print.print_warning("Timeout, IP addresses not yet assigned.")
        else:
            Print.print_error("No Deployment with name {name}".format(name=deployment_name))

    @staticmethod
    def stop(deployment_name):
        """Shutdown virtual machines."""
        hosts = Hosts().get_deployment_by_name(deployment_name)
        if hosts:
            # Start the thread executor
            executor = ThreadPoolExecutor(max_workers=3)
            threads = []
            # Assign each host shutdown command to a thread
            for host in hosts:
                t = executor.submit(host.stop)
                threads.append(t)
            # Wait for all threaded processes to complete
            for thread in threads:
                thread.result()
        else:
            Print.print_error("No Deployment with name {name}".format(name=deployment_name))

    @staticmethod
    def restart(deployment_name):
        """Restart virtual machines."""
        hosts = Hosts().get_deployment_by_name(deployment_name)
        if hosts:
             # Start the thread executor
            executor = ThreadPoolExecutor(max_workers=len(hosts))
            threads = []
            # Assign each host restart command to a thread
            for host in hosts:
                t = executor.submit(host.restart)
                threads.append(t)
            # Wait for all threaded processes to complete
            for thread in threads:
                thread.result()
        else:
           Print.print_error("No Deployment with name {name}".format(name=deployment_name))

    @staticmethod
    def destroy(deployment_name):
        """Permanently delete all virtual machines and networks."""
        hosts = Hosts().get_deployment_by_name(deployment_name)
        if hosts:

            # Ensure all virtual machines are powered down
            Topology.stop(deployment_name)
            # Start the thread executor
            executor = ThreadPoolExecutor(max_workers=len(hosts))
            threads = []
            # Assign each host destroy command to a thread
            for host in hosts:
                t = executor.submit(host.destroy)
                threads.append(t)
            # Wait for all threaded processes to complete
            for thread in threads:
                thread.result()
            executor.shutdown(wait=True)

            # Delete host database entry
            for host in hosts:
                Session.delete(host)
                Session.commit()

            # Get the networks from the database
            networks = Networks().get_deployment_by_name(deployment_name)

            if networks:
                # Start the thread executor
                executor = ThreadPoolExecutor(max_workers=len(networks))
                threads = []
                # Assign each network destroy command to a thread
                for network in networks:
                    t = executor.submit(network.destroy)
                    threads.append(t)
                # Wait for all threaded processes to complete
                for thread in threads:
                    thread.result()
                executor.shutdown(wait=True)

                # Delete network database entry
                for network in networks:
                    Session.delete(network)
                    Session.commit()

            # Delete deployment
            Deployments().delete_by_name(deployment_name)
        else:
            Print.print_error("No Deployment with name {name}".format(name=deployment_name))

    @staticmethod
    def host_details():
        """Return summary of all host properties."""
        # Get the hosts from the database
        hosts = Hosts().get_all()

        # Table data, each row is a list
        data = []
        for host in hosts:
            s = {}
            s["vmname"] = host.vmname
            s.update(host.properties())
            del s['nics']
            s['deployment'] = Deployments.get_by_id(host.deployment_id).name
            data.append(s)
       
        return data

    @staticmethod
    def network_details():
        """Return summary of all host-network configurations."""
        # Get the hosts from the database
        hosts = Hosts().get_all()
        # Table data, each row is a list
        data = []

        for host in hosts: 
            nics = host.properties()["nics"]
            for nic in nics.keys():
                n = {}
                n["vmname"] = host.vmname
                n["name"] = nic
                n["netname"] = nics[nic]["netname"]
                n["mac"] = nics[nic]["mac"]
                n["ip"] = nics[nic]["ip"]
                n['deployment'] = Deployments.get_by_id(host.deployment_id).name
                data.append(n)
        return data

    @staticmethod
    def shell(vmname):
        """
        Create an SSH shell terminal sessions with each host.
        Support for Mac and Linux (Gnome) only.
        """
        host = Hosts().get_vmname(vmname)
        if host:
            host.ssh()
        else:
            raise Exception("Unknown vmname entered.")

    @staticmethod
    def send_keys(deployment_name):
        """Generate and distribute SSH public keys to hosts."""
        hosts = Hosts().get_deployment_by_name(deployment_name)
        if hosts:
            for host in hosts:
                host.dist_pkey()
        else:
            Print.print_error("No Deployment with name {name}".format(name=deployment_name))
    
    @staticmethod
    def start_ssh_forwarder(deployment_name):
        """Start ssh forwarder server for connection to vm through host machine."""
        hosts = Hosts().get_deployment_by_name(deployment_name)
        if hosts:
            for host in hosts:
                host.ssh_forwarder() 
        else:
            Print.print_error("No Deployment with name {name}".format(name=deployment_name))

    @staticmethod
    def stop_ssh_forwarders(deployment_name):
        """Stop any running ssh forwardingservers"""
        #Loop through the sshforwarders running
        for server in SSHForward.get_by_deployment(deployment_name):
            try:
                os.kill(server.pid, 9)
                SSHForward.delete(server)
            except ProcessLookupError:
                print ("here")
                pass
           
