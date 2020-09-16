from pathlib import Path
import xml.etree.ElementTree as ET
import subprocess
import re
import time
import sys
from print_colours import Print

# Create ObjectRelationalModel (ORM) base class
from sqlalchemy import Column, Integer, String, Sequence
from db import Base, Session

class Network(Base):
    # Define 'network' SQL table for instances of Host
    __tablename__ = 'networks'
    id = Column(Integer, Sequence('network_id_seq'), primary_key=True)
    label = Column(String, unique=True)
    netname = Column(String, unique=True)
    netaddr = Column(String)
    dhcplower = Column(String)
    dhcpupper = Column(String)

    def __repr__(self):
        return "<Network(label='%s', netname='%s', netaddr='%s', dhcplower='%s', dhcpupper='%s')>" % (
            self.label, self.netname, self.netaddr, self.dhcplower, self.dhcpupper)

    def __init__(self, label, netaddr, dhcplower, dhcpupper):
        """
        Initialises VirtualBox host-only network interface
        Options:
            label: user defined label to identify network interface
            netname: name of host only interface
            hostaddr: address of the interface
            dhcplower: Lower range of assignable ip addresses
            dhcpupper: Upper range of assignable ip addresses
        """
        self.label = label
        self.netname = self.next_name() # recieve name from VirtualBox
        self.netaddr = netaddr
        self.dhcplower = dhcplower
        self.dhcpupper = dhcpupper
        # Call VirtualBox to create network
        self.create()

    @classmethod
    def check_exists(self, netname):
        """
        Check if network already exists.
        """
        r = subprocess.getoutput("vboxmanage list hostonlyifs|grep '" + netname + "'")
        if (r != ""):
            return True

    @classmethod
    def get_dhcp_leases(self, netname):
        """
        Retreive DHCP leases as a dictionary {mac: ip,}
        """
        leases = {}
        # Linux config location ~/.config/VirtualBox/...
        if sys.platform == "darwin":
            # Mac config location ~/Library/VirtualBox
            path = Path.home().glob('Library' + '/VirtualBox' + '/HostInterfaceNetworking-' + netname + '-Dhcpd.leases')
        elif sys.platform == "linux":
            # Linux config location ~/.config/VirtualBox/...
            path = Path.home().glob('.config' + '/VirtualBox' + '/HostInterfaceNetworking-' + netname + '-Dhcpd.leases')
        else:
            raise Exception("OS not supported")

        for filepath in path:
            # create element tree object
            root = ET.parse(str(filepath)).getroot()
            # Loop through the hosts and find assigned IP
            for lease in root.findall('Lease'):
                if lease.attrib["state"] != "expired":
                    macaddr = lease.attrib["mac"]
                    leases[macaddr] = lease.find('Address').attrib['value']
        return leases

    def get_name(self):
        """
        Return the name of the network as assigned by VirtualBox.
        """
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
            bigid = netids[-1] # largest id assigned
        for n in range(0, bigid + 2): # search for smallest unused id, up to 1 greater than the largest
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
        # Enable the server
        cmd = 'VBoxManage dhcpserver modify --ifname '+ self.netname +' --disable'
        subprocess.getoutput(cmd)
        time.sleep(20)
        cmd = 'VBoxManage dhcpserver modify --ifname '+ self.netname +' --enable'
        subprocess.getoutput(cmd)

    def destroy(self):
        """
        Permanently destroy host-only network.
        """
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
        # Delete database entry
        ####

    def dict(self):
        """
        Return an ordered dictionary for printing purposes
        """
        # Get the dict and organised keys
        dict = self.__dict__
        keys = ["id", "label", "netname", "netaddr", "dhcplower", "dhcpupper"]

        # Create and return a new dictionary
        new_dict= {}
        for key in keys:
            new_dict[key] = dict[key]

        return new_dict

    def write_to_db(self):
        """
        Write the network to the database
        """
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
