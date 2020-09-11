import os
from concurrent.futures import ThreadPoolExecutor
import time
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
from tabulate import tabulate
import traceback

from network import Network 
from host import Host 

class Topology():
    """
    Launch a network toplogy using VirtualBox 
    """

    def __init__(self):
        """
        Initialise network, simple master (1) slave (2) configuration. 
        """
        self.hosts = {}
        self.networks = {}
        # Create network(s) 
        n1 = Network("20.0.0.1", "20.0.0.2", "20.0.0.254")
        self.networks[n1.get_name()] = n1
        # Create host(s) 
        self.hosts["master"] = Host("master", "Ubuntu Server 20.04")
        self.hosts["slave1"] = Host("slave1", "Ubuntu Server 20.04")
        self.hosts["slave2"] = Host("slave2", "Ubuntu Server 20.04")
        # Assign NAT for internet access 
        self.hosts["master"].assign_internet(1) 
        self.hosts["slave1"].assign_internet(1) 
        self.hosts["slave2"].assign_internet(1) 
        # Assign to local network 
        self.hosts["master"].assign_network(2, n1.get_name())
        self.hosts["slave1"].assign_network(2, n1.get_name())
        self.hosts["slave2"].assign_network(2, n1.get_name())
    
    def start(self):
        """
        Start virtual network and machines. 
        """
        # Start the thread executor
        executor = ThreadPoolExecutor(max_workers=len(self.hosts.keys()))
        threads = []
        # Assign each host start command to a thread
        for host in self.hosts.values():
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
        t = time.time() 
        hosts = list(self.hosts.values())[:]
        while time.time() - t < timeout and len(hosts) > 0: 
            time.sleep(1) 
            for host in hosts: 
                if host.get_ip():
                    hosts.remove(host)
        if len(hosts) > 0:
            print("[!] Timeout, IP addresses not yet assigned.") 

    def stop(self):
        """
        Shutdown virtual machines. 
        """
        # Start the thread executor
        executor = ThreadPoolExecutor(max_workers=3)
        threads = []
        # Assign each host shutdown command to a thread 
        for host in self.hosts.values():
            t = executor.submit(host.stop)
            threads.append(t)
        # Wait for all threaded processes to complete
        for thread in threads:
            thread.result()
    
    def destroy(self):
        """
        Permanently delete all virtual machines and networks. 
        """
        # Ensure all virtual machines are powered down 
        self.stop() 
        # Start the thread executor
        executor = ThreadPoolExecutor(max_workers=5)
        threads = []
        # Assign each host destroy command to a thread 
        for host in self.hosts.values():
            t = executor.submit(host.destroy)
            threads.append(t)
        # Wait for all threaded processes to complete
        for thread in threads:
            thread.result() 
        # Assign each network destroy command to a thread 
        threads = []
        for network in self.networks.values():
            t = executor.submit(network.destroy)
            threads.append(t)
        # Wait for all threaded processes to complete
        for thread in threads:
            thread.result() 
    
    def show_hosts(self):
        """
        Return summary of all host properties. 
        """
        # Table header
        header = ["vmname", "VMState", "ostype", "cpus", "memory"]
        # Table data, each row is a list 
        rows = []
        for host in self.hosts.values():
            s = host.properties()  
            row = [host.vmname] + [s[h] for h in header[1:]]
            rows.append(row) 
        summary = tabulate(rows, header, tablefmt="fancy_grid")
        print(summary) 
    
    def show_networks(self): 
        """
        Return summary of all host-network configurations. 
        """
        # Table header
        header = ["vmname", "nic", "netname", "mac", "ip"]
        # Table data, each row is a list 
        rows = []
        for host in self.hosts.values():
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
        if vmname in self.hosts.keys():
            self.hosts[vmname].ssh() 
        elif vmname == 'all':
            for host in self.hosts.values(): 
                host.ssh() 
        else:
            raise Exception("[!] Unknown vmname entered.")
    
    def send_keys(self):
        """
        Distribute SSH public keys to hosts. 
        Support for Mac only. 
        """
        for host in self.hosts.values(): 
            host.dist_pkey() 


################################################################################
# Main
################################################################################

if __name__ == '__main__':
    t = Topology()
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



