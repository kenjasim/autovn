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
from resources import Hosts, Networks, Deployments
from constructor import Constructor
from print_colours import Print

from db import Session, create_tables, close_database, return_tables

class Topology():
    """
    Launch a network toplogy using VirtualBox
    """

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
    def start(deployment_id):
        """
        Start virtual network and machines.
        """
        # Get the hosts from the database
        hosts = Hosts().get_deployment(deployment_id)
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
            Topology.poll_ips(deployment_id)
        else:
            Print.print_error("No Deployment with id {id}".format(id=deployment_id))

    @staticmethod
    def poll_ips(deployment_id, timeout=30):
        """
        Poll hosts for IP assignment.
        """
        # Get the hosts from the database
        hosts = Hosts().get_deployment(deployment_id)
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
            Print.print_error("No Deployment with id {id}".format(id=deployment_id))

    @staticmethod
    def stop(deployment_id):
        """
        Shutdown virtual machines.
        """
        hosts = Hosts().get_deployment(deployment_id)
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
            Print.print_error("No Deployment with id {id}".format(id=deployment_id))

    
    @staticmethod
    def restart(deployment_id):
        """
        Restart virtual machines.
        """
        hosts = Hosts().get_deployment(deployment_id)
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
            Print.print_error("No Deployment with id {id}".format(id=deployment_id))

       

    @staticmethod
    def destroy(deployment_id):
        """
        Permanently delete all virtual machines and networks.
        """
        hosts = Hosts().get_deployment(deployment_id)
        if hosts:

            # Ensure all virtual machines are powered down
            Topology.stop(deployment_id)
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
            networks = Networks().get_deployment(deployment_id)

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
            Deployments().delete_by_id(deployment_id)
        else:
            Print.print_error("No Deployment with id {id}".format(id=deployment_id))

    @staticmethod
    def host_details():
        """
        Return summary of all host properties.
        """
        # Get the hosts from the database
        hosts = Hosts().get_all()

        # Table data, each row is a list
        data = []
        for host in hosts:
            s = {}
            s["vmname"] = host.vmname
            s.update(host.properties())
            del s['nics']
            s['deployment'] = host.deployment_id
            data.append(s)
       
        return data

    @staticmethod
    def network_details():
        """
        Return summary of all host-network configurations.
        """
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
                data.append(n)
        return data

    @staticmethod
    def shell(vmname):
        """
        Create an SSH shell terminal sessions with each host.
        Support for Mac only.
        Options:
            vmname: name of rm to create shell session for
        """
        host = Hosts().get_vmname(vmname)
        if host:
            host.ssh()
        else:
            raise Exception("Unknown vmname entered.")

    @staticmethod
    def send_keys(deployment_id):
        """
        Distribute SSH public keys to hosts.
        """
        hosts = Hosts().get_deployment(deployment_id)
        if hosts:
            for host in hosts:
                host.dist_pkey()
        else:
            Print.print_error("No Deployment with id {id}".format(id=deployment_id))

        





################################################################################
# Main
################################################################################

if __name__ == '__main__':
    pass

################################################################################
# Resources
################################################################################
