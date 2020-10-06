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
from resources import Hosts, Networks
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

        # Check the db before building
        if Hosts().check_database():
            raise Exception ("Database already contains host, please consider destroying")

        # Check if the file exits, if not then raise an exception
        Constructor(template_file).parse()
    
    @staticmethod
    def start():
        """
        Start virtual network and machines.
        """
        # Get the hosts from the database
        hosts = Hosts().get_all()

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
        Topology.poll_ips()

    @staticmethod
    def poll_ips(timeout=30):
        """
        Poll hosts for IP assignment.
        """
        # Get the hosts from the database
        hosts = Hosts().get_all()

        t = time.time()
        while time.time() - t < timeout and len(hosts) > 0:
            time.sleep(1)
            for host in hosts:
                if host.get_ip():
                    hosts.remove(host)
        if len(hosts) > 0:
            Print.print_warning("Timeout, IP addresses not yet assigned.")

    @staticmethod
    def stop():
        """
        Shutdown virtual machines.
        """
        # Get the hosts from the database
        hosts = Hosts().get_all()

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
    
    @staticmethod
    def restart():
        """
        Restart virtual machines.
        """
        # Get the hosts from the database
        hosts = Hosts().get_all()
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

    @staticmethod
    def destroy():
        """
        Permanently delete all virtual machines and networks.
        """
        if Hosts().check_database():
            # Get the hosts from the database
            hosts = Hosts().get_all()

            # Ensure all virtual machines are powered down
            Topology.stop()
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
            networks = Networks().get_all()

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
        # Destroy database
        datapath = Path().parent.absolute() / "tmp" / "data.db"
        if os.path.isfile(str(datapath)):
            os.remove(str(datapath))

    @staticmethod
    def show_hosts():
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
            data.append(s)
       
        return data

    @staticmethod
    def show_networks():
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
    def shell(vmname='all'):
        """
        Create an SSH shell terminal sessions with each host.
        Support for Mac only.
        Options:
            vmname: name of rm to create shell session for
        """
        host = Hosts().get_vmname(vmname)
        if vmname == 'all':
            # Get the hosts from the database
            hosts = Hosts().get_all()
            for host in hosts:
                host.ssh()
        elif host:
            host.ssh()
        else:
            raise Exception("Unknown vmname entered.")

    @staticmethod
    def send_keys(vmname):
        """
        Distribute SSH public keys to hosts.
        """
        # Get the hosts from the database
        hosts = Hosts().get_all()
        for host in hosts:
            if vmname == "all" or host.get_vmname() == vmname:
                host.dist_pkey()





################################################################################
# Main
################################################################################

if __name__ == '__main__':
    t = Topology("k8")
    t.start()
    t.show_hosts()
    t.show_networks()
    time.sleep(10)
    t.shell()
    print("close (y/n):")
    a = input()
    if a == 'y':
        t.destroy()


################################################################################
# Resources
################################################################################
