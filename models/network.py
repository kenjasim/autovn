from pathlib import Path
import xml.etree.ElementTree as ET
import subprocess
import re
import time
import sys

from sqlalchemy import Column, Integer, String, Sequence, ForeignKey
from db import Base, Session
from print_colours import Print

class Network(Base):
    """
    Network object to represent real Virtual Networks.
    """
    # Define 'networks' SQL table for instances of Network
    __tablename__ = 'networks'
    id = Column(Integer, Sequence('network_id_seq'), primary_key=True)
    label = Column(String)
    netname = Column(String, unique=True)
    netaddr = Column(String, unique=True)
    dhcplower = Column(String)
    dhcpupper = Column(String)
    deployment_id = Column(Integer, ForeignKey('deployments.id'))

    def __init__(self, label, netaddr, dhcplower, dhcpupper, deployment_id):
        """
        Initialises VirtualBox host-only network interface.
        Options:
            label           (str): user defined label to identify network interface
            hostaddr        (str): address of the interface 
            dhcplower       (str): Lower range of assignable ip addresses
            dhcpupper       (str): Upper range of assignable ip addresses
            deployment_id   (int): ID for the deployment group
        """
        self.label = label
        # recieve name from VirtualBox
        self.netname = self.next_name() 
        self.netaddr = netaddr
        self.dhcplower = dhcplower
        self.dhcpupper = dhcpupper
        self.deployment_id = deployment_id
        # Call VirtualBox to create network
        self.create()

    @classmethod
    def check_exists(self, netname):
        """Check if network already exists, if present returns True"""
        r = subprocess.getoutput("vboxmanage list hostonlyifs|grep '" + netname + "'")
        if (r != ""):
            return True

    @classmethod
    def get_dhcp_leases(self, netname):
        """
        Retreive DHCP leases.
        Returns:
            leases  (dict): {mac: ip}
        """
        leases = {}
        if sys.platform == "darwin":
            # Mac config location ~/Library/VirtualBox
            path = Path.home().glob('Library' + '/VirtualBox' + '/HostInterfaceNetworking-' + netname + '-Dhcpd.leases')
        elif sys.platform == "linux":
            # Linux config location ~/.config/VirtualBox/...
            path = Path.home().glob('.config' + '/VirtualBox' + '/HostInterfaceNetworking-' + netname + '-Dhcpd.leases')
        else:
            raise Exception("OS not supported")

        for filepath in path:
            # Create element tree object
            root = ET.parse(str(filepath)).getroot()
            # Loop through the hosts and find assigned IP
            for lease in root.findall('Lease'):
                if lease.attrib["state"] != "expired":
                    macaddr = lease.attrib["mac"]
                    leases[macaddr] = lease.find('Address').attrib['value']
        return leases

    def get_name(self):
        """Return the name of the network as assigned by VirtualBox."""
        return self.netname

    def next_name(self):
        """
        Identify next host-only network interface name to be assigned by VBox
        Note, VirtualBox increments host-only names, e.g. "vboxnetN"
        Limited to 128 host-only network interfaces.
        """
        r = subprocess.getoutput("vboxmanage list hostonlyifs|grep HostInterfaceNetworking-vboxnet")
        netnames = r.splitlines()
        netids = [int(re.match('.*?([0-9]+)$', name).group(1)) for name in netnames]
        netids.sort()
        bigid = 0
        if len(netids) != 0:
            bigid = netids[-1] # Largest id assigned
        # Search for smallest unused id, up to 1 greater than the largest
        for n in range(0, bigid + 2): 
            if n not in netids:
                return "vboxnet" + str(n)
        raise Exception("[!] Failed to find a free network name.")

    def create(self):
        """
        Create host-only network interface.
        Note, VirtualBox increments host-only names, e.g. "vboxnetN"
        """
        # Check if network name is avaliable
        if self.check_exists(self.netname):
            raise Exception("Network with name " + self.netname + " already exists.")
        # Create host-only network interface
        subprocess.getoutput("VBoxManage hostonlyif create")
        # Check if network has been created
        if not self.check_exists(self.netname):
            raise Exception("Failed to create network with name " + self.netname)
        # Set IP address of the host-only network interface
        cmd = 'VBoxManage hostonlyif ipconfig ' + self.netname + ' --ip ' + self.netaddr
        subprocess.getoutput(cmd)
        # Create the DHCP server
        cmd = 'VBoxManage dhcpserver add --ifname '+ self.netname
        cmd += ' --ip ' + self.netaddr
        cmd += ' --netmask 255.255.255.0'
        cmd += ' --lowerip ' + self.dhcplower
        cmd += ' --upperip ' + self.dhcpupper
        subprocess.getoutput(cmd)
        # Enable the server
        cmd = 'VBoxManage dhcpserver modify --ifname '+ self.netname +' --enable'
        subprocess.getoutput(cmd)
        Print.print_success("Created network " + self.netname)

    def reset_dhcp(self):
        """Call DHCP server to reset."""
        # Disable the DHCP server
        cmd = 'VBoxManage dhcpserver modify --ifname '+ self.netname +' --disable'
        subprocess.getoutput(cmd)
        time.sleep(20)
        # Re-enable the DHCP server
        cmd = 'VBoxManage dhcpserver modify --ifname '+ self.netname +' --enable'
        subprocess.getoutput(cmd)

    def destroy(self):
        """Permanently destroy host-only network."""
        # Destroy DHCP server
        cmd = 'VBoxManage dhcpserver remove --interface ' + self.netname
        subprocess.getoutput(cmd)
        # Delete DHCP logs and lease config files
        if sys.platform == "darwin":
            # Mac config location ~/Library/VirtualBox
            path = Path.home().glob('Library' + '/VirtualBox' + '/HostInterfaceNetworking-' + self.netname + '-Dhcpd.*')
        elif sys.platform == "linux":
            # Linux config location ~/.config/VirtualBox/...
            path = Path.home().glob('.config' + '/VirtualBox' + '/HostInterfaceNetworking-' + self.netname + '-Dhcpd.*')
        else:
            raise Exception("OS not supported")
        for filepath in path:
            cmd = 'rm ' + str(filepath)
            subprocess.getoutput(cmd)
        # Destroy host-only network interface
        cmd = 'VBoxManage hostonlyif remove ' + self.netname
        subprocess.getoutput(cmd)
        # Set network object properties to None (indicate deleted)
        self.netname = None
        self.netaddr = None
        Print.print_success("Destroyed network ")

    def dict(self):
        """Return an ordered dictionary of network properties for printing purposes."""
        # Get the dict and organised keys
        cdict = self.__dict__
        # Create and return a new dictionary
        keys = ["id", "label", "netname", "netaddr", "dhcplower", "dhcpupper"]
        new_dict= {}
        for key in keys:
            new_dict[key] = cdict[key]
        return new_dict

    def write_to_db(self):
        """Write the network to the database"""
        Session.add(self)
        Session.commit()


################################################################################
# Main
################################################################################

if __name__ == '__main__':
    n = Network("20.0.0.1", "20.0.0.2", "20.0.0.254")


################################################################################
# Resources
################################################################################
