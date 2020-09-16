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

    def __init__(self):
        # Create SQL tables for networks and hosts
        create_tables()

    def build(self, template_file="templates/default.yaml"):
        """
        Read a yaml configuration file to get the network required and then
        initialise the network
        """
        # Check the db before building
        if Hosts().check_database():
            raise Exception ("Database already contains host, please consider destroying")

        # Check if the file exits, if not then raise an exception
        if (os.path.isfile(template_file)):
            Constructor(template_file).parse()
        else:
            raise Exception("Failed to find the file " + template_file)

    def start(self):
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
        self.poll_ips()

    def poll_ips(self, timeout=30):
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

    def stop(self):
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

    def destroy(self):
        """
        Permanently delete all virtual machines and networks.
        """
        if Hosts().check_database():
            # Get the hosts from the database
            hosts = Hosts().get_all()

            # Ensure all virtual machines are powered down
            self.stop()
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

    def show_hosts(self):
        """
        Return summary of all host properties.
        """
        # Get the hosts from the database
        hosts = Hosts().get_all()
        # Table header
        header = ["vmname", "VMState", "ostype", "cpus", "memory"]
        # Table data, each row is a list
        rows = []
        for host in hosts:
            s = host.properties()
            row = [host.vmname] + [s[h] for h in header[1:]]
            rows.append(row)
        summary = tabulate(rows, header, tablefmt="fancy_grid")
        print(summary)

    def show_networks(self):
        """
        Return summary of all host-network configurations.
        """
        # Get the hosts from the database
        hosts = Hosts().get_all()
        # Table header
        header = ["vmname", "nic", "netname", "mac", "ip"]
        # Table data, each row is a list
        rows = []
        for host in hosts:
            nics = host.properties()["nics"]
            for nic in nics.keys():
                row = [host.vmname, nic] + [nics[nic][h] for h in header[2:]]
                rows.append(row)
        summary = tabulate(rows, header, tablefmt="fancy_grid")
        print(summary)

    def shell(self, vmname='all'):
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

    def send_keys(self):
        """
        Distribute SSH public keys to hosts.
        Support for Mac only.
        """
        # Get the hosts from the database
        hosts = Hosts().get_all()

        for host in hosts:
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
