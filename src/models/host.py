from pathlib import Path
import subprocess
import re
import os
import time
import netifaces
from models.network import Network
from models.port_forward import PortForward
from tabulate import tabulate
from autossh import ssh_shell
from print_colours import Print

from sqlalchemy import Column, Integer, String, Sequence, ForeignKey
from db import Base
from db import Session

class Host(Base):
    """
    Host object to represent real Virtual Host OS.
    """
    # Define 'hosts' SQL table for instances of Host
    __tablename__ = 'hosts'
    id = Column(Integer, Sequence('host_id_seq'), primary_key=True)
    vmname = Column(String, unique=True)
    image = Column(String)
    username = Column(String)
    password = Column(String)
    deployment_id = Column(Integer, ForeignKey('deployments.id'))
    ssh_remote_port = Column(Integer, unique=True)

    def __init__(self, vmname, image, username, password, deployment_id):
        """
        Initialises Ubuntu Server 20.04 virtual machine via VirtualBox
        Options:
            label       (str): user defined label to identify host
            image       (str): name of the .ova image located in vm_templates directory
            username    (str): username of the machine
            password    (str): password of the machine
        """
        self.vmname = vmname
        self.image = image
        self.username = username
        self.password = password
        self.deployment_id = deployment_id
        self.ssh_port = None
        # Check if image template or vmname already exists
        if self.check_exists(image):
            raise Exception("Template image already exists, unable to duplicate")
        if self.check_exists(vmname):
            raise Exception("VM image with assigned name already exists")
        # Import image into VirtualBox
        self.import_image()
        # Write to database
        try:
            self.write_to_db()
        except Exception as e:
            raise Exception("Faied to add host model to database: " + repr(e))

    @classmethod
    def check_exists(self, vmname):
        """Check if a virtual machine with the given label exists."""
        # Collate list of currently imported vm names
        cmd = ['vboxmanage list vms']
        vmsfound = re.findall(r"\"(.*)\"", subprocess.getoutput(cmd))
        # Check if any match
        for name in vmsfound:
            if vmname == name:
                return True

    def import_image(self):
        """Import vm .ova image into VirtualBox"""
        # Get the images folder
        images_path = Path().home() / ".avn" / "images" / self.image
        # Check image exists
        if not os.path.isfile(images_path):
            raise Exception("Virtual machine '.ova'. template not found")
        # Form path to image
        try:
            cmd = 'VBoxManage import ' + "\"" + str(images_path) + "\"" + ' --vsys 0 --vmname ' + self.vmname
            subprocess.getoutput(cmd)
        except Exception as e:
            raise Exception("Failed to import image") 

        # Check vm successfully imported
        if not self.check_exists(self.vmname):
            raise Exception("Failed to import virtual machine.")
        else:
            Print.print_success("Successfully imported machine " + self.vmname)

    def assign_network(self, adapter, netname):
        """
        Assign a virtual machine adapter to a network
        Options:
            adapter (str): Adapter of host to be used, e.g. 1 to 8
            netname (str): Name of the host-only network to connect to
        """
        # Check network exists
        if not Network.check_exists(netname):
            raise Exception("Unable to assign network, does not exist.")
        # Set network interface type to host-only
        cmd = 'vboxmanage modifyvm ' + self.vmname + ' --nic' + str(adapter) + ' hostonly'
        subprocess.getoutput(cmd)
        # Assign network interface adapter to the host-only network
        cmd = 'vboxmanage modifyvm ' + self.vmname + ' --hostonlyadapter' + str(adapter) + ' ' + netname
        subprocess.getoutput(cmd)

    def assign_internet(self, adapter, nettype='bridged'):
        """
        Assign a 'bridged' or 'nat' interface to the virtual machines for internet.
        If 'bridged', IP address is assigned by the gateway router. 
        Options:
            adapter (int): Adapter of host to be used, e.g. 1 to 8
            nettype    (str): Network type ('bridged' or 'nat')
        """
        # Identify default host's default gateway interface 
        iface = None
        try:            
            iface = netifaces.gateways()['default'][netifaces.AF_INET][1]
        except Exception as e:
            Print.print_warning("Failed to identify interface in 'default'")
            try:
                iface = netifaces.gateways()[netifaces.AF_INET][0][1]
                Print.print_success("Interface identified")
            except Exception as e:
                raise Exception("failed to retrieve interface name" + repr(e)) 
        # Build command for assigning adapter to interface
        if nettype == 'nat':
            try:
                cmd = 'vboxmanage modifyvm ' + self.vmname + ' --nic' + str(adapter) + ' ' + 'nat'
                # Assign network interface 
                subprocess.getoutput(cmd)
            except Exception as e:
                raise Exception("failed to assign nat adapter " + repr(e))
        elif nettype == 'bridged':
            try:
                cmd = 'vboxmanage modifyvm ' + self.vmname + ' --nic' + str(adapter) + ' ' + nettype + " --bridgeadapter2 " + "'" + iface + "'"
                # Assign network interface 
                subprocess.getoutput(cmd)
            except Exception as e:
                raise Exception("failed to assign bridged adapter " + repr(e)) 
        else: 
            raise Exception("Invalid nettype, please choose between 'bridged' and 'nat'.")

    def properties(self):
        """
        Retrieve configuration properties for the virtual machine.
        Returns dict {"VMState": , "ostype": , "cpus":, "memory": }
        """
        # Get individual vm data
        cmd = 'vboxmanage showvminfo ' +  self.vmname + ' --machinereadable'
        info = subprocess.getoutput(cmd).splitlines()
        # Parse data
        dinfo = {"VMState": None, "ostype": None, "cpus": None, "memory": None, "nics": {}}
        for entry in info:
            key = entry.split("=")[0]
            value = entry.split("=")[1].replace('"', "")
            if key in dinfo.keys():
                dinfo[key] = value
            # Identify network connections
            if "hostonlyadapter" in key or "natnet" in key or "bridgeadapter" in key:
                nic = re.match('.*?([0-9]+)$', key).group(1)
                dinfo["nics"][nic] = {"netname": value, "mac": None, "ip": None}
        # Identify MAC addresses
        for entry in info:
            key = entry.split("=")[0]
            value = entry.split("=")[1].replace('"', "")
            if "macaddress" in key:
                nic = re.match('.*?([0-9]+)$', key).group(1)
                # Format MAC address to lower case with colons
                mac = ':'.join(value.strip('"').lower()[i:i+2] for i in range(0,12,2))
                dinfo["nics"][nic]["mac"] = mac
        # Identify IP addresses
        for nic in dinfo["nics"].values():
            netname = nic["netname"]
            mac = nic["mac"]
            if mac in Network.get_dhcp_leases(netname).keys():
                nic["ip"] = Network.get_dhcp_leases(netname)[mac]
        return dinfo

    def get_ip(self):
        """
        Return first assigned IP address.
        """
        p = self.properties()
        for nic in p["nics"].values():
            if nic["ip"] is not None:
                return nic["ip"]

    def get_username(self):
        """Return host username."""
        return self.username
    
    def get_vmname(self):
        """Return host vmname."""
        return self.vmname
    
    def get_ssh_remote_port(self):
        """Return host's ssh_remote_port"""
        return self.ssh_remote_port

    def start(self, headerless=True):
        """
        Start running virtual machine.
        Options:
            headerless (bool): run without VirtualBox display (default is True)
        """
        # Set headerless option and start VM
        cmd = 'VBoxManage startvm ' + self.vmname
        if headerless:
            cmd += ' --type headless'
        r = subprocess.getoutput(cmd)
        # Check if successfull
        if "successfully started" not in r:
            raise Exception("Failed to start virtual machine: " + r)

        Print.print_success("Launched machine " + self.vmname)

    def stop(self):
        """Shutdown the virtual machine."""
        cmd = 'VBoxManage controlvm ' + self.vmname + ' poweroff'
        subprocess.getoutput(cmd)
        Print.print_success("Powered off machine " + self.vmname)

    def restart(self):
        """Power off and on again the virtual machine."""
        # Call host to poweroff 
        self.stop()
        # Wait for VM to poweroff 
        t = time.time() 
        while time.time() - t < 30:
            state = self.properties()["VMState"]
            if state == "poweroff":
                break
        time.sleep(3) 
        self.start()

    def destroy(self):
        """Permanently delete the virtual machine and all it's files."""
        # Delete SSH known_hosts entry
        if self.get_ip():
            cmd = "sed -i '' '/" + self.get_ip() + "/d' ~/.ssh/known_hosts"
            subprocess.getoutput(cmd)
        # Delete virtual machine from VirtualBox
        cmd = 'VBoxManage unregistervm --delete ' + self.vmname
        subprocess.getoutput(cmd)
        # Show status
        Print.print_success("Destroyed machine " + self.vmname)

    def ssh(self):
        """Launch SSH session with host."""
        shell = ssh_shell.Shell()
        # Retrieve IP address
        ip = self.get_ip()
        if ip is None:
            raise Exception("IP address not assigned.")
        # Open SSH session through new terminal
        shell.connect(hostname=self.username, hostaddr=ip, password=self.password, hostport=22)

    def dist_pkey(self):
        """Create and distribute SSH keys for/to the host."""
        p = Path().home() / ".avn" / "keys"
        keyname = "id_rsa_vb"
        # Check keys path exists, else create 
        if not os.path.isdir(str(p)): 
            os.mkdir(str(p)) 
        # Check if key already exists
        ap = p / keyname
        if not ((os.path.isfile(str(ap))) or (os.path.isfile(str(ap) + ".pub"))):
            # Create RSA key pair
            cmd = "ssh-keygen -t rsa -b 4096 -q -N \"\" -f " + str(ap)
            subprocess.getoutput(cmd)
        if not ((os.path.isfile(str(ap))) or (os.path.isfile(str(ap) + ".pub"))):
            raise Exception("RSA key pair generation failed.")
        # Add private key the SSH agent
        cmd = "eval `ssh-agent`"
        subprocess.getoutput(cmd)
        cmd = "ssh-add " + str(ap)
        subprocess.getoutput(cmd)
        # Share public key with host
        shell = ssh_shell.Shell()
        ip = self.get_ip()
        r = shell.copy(hostname=self.username, hostaddr=ip, password=self.password, keypath=(str(ap) + ".pub"))
        if "try logging" not in r:
            raise Exception("Failed to distribute SSH public key to host.")
        else:
            Print.print_success("SSH key distributed to host " + self.vmname + " at " + self.username + "@" + self.get_ip())

    def ssh_forwarder(self): 
        """
        Run a background server to forward SSH traffic between the host machine
        and the virtual machine. 
        """
        shell = PortForward(self.deployment_id)
        # Find an unassigned port 
        host_port = 2000
        while shell.port_in_use(host_port):
            host_port += 1
        self.ssh_remote_port = host_port
        Print.print_information("SSH port assigned to " + self.vmname + ": " + str(host_port))
        ip = self.get_ip()
        shell.start_forwarding_server(host_port=host_port, dest_addr=ip) 
        self.update_to_db() 
    
    def proxy_ssh(self, public_ip):
        """
        Launch SSH session with virtual machine via host system. 
        Relies on ssh_forwarder Server to be active. 
        """
        shell = ssh_shell.Shell()
        # Open SSH session through new terminal
        shell.connect(hostname=self.username, hostaddr=public_ip, password=self.password, hostport=self.ssh_remote_port)

    def __str__(self):
        """
        Print Host properties to console.
        """
        info = self.properties()
        header = ["vmname", "VMState", "ostype", "cpus", "memory"]
        data = [self.vmname] + [info[k] for k in header[1:]]
        s = tabulate([data], header,tablefmt="fancy_grid") + "\n"
        netinfo = info["nics"]
        header = ["nic", "netname", "mac", "ip"]
        data = []
        for nic in netinfo.keys():
            row = [nic] + [netinfo[nic][k] for k in header[1:]]
            data.append(row)
        s += tabulate(data, header,tablefmt="fancy_grid")
        return s

    def dict(self):
        """Return an ordered dictionary for printing purposes."""
        # Get the dict and organised keys
        dict = self.__dict__
        keys = ["id", "vmname", "image", "username"]

        # Create and return a new dictionary
        new_dict= {}
        for key in keys:
            new_dict[key] = dict[key]
        return new_dict

    def write_to_db(self):
        """Write the host to the database."""
        Session.add(self)
        Session.commit()
    
    def update_to_db(self):
        """Update the host to the database."""
        Session.commit()


################################################################################
# Resources
################################################################################

# https://en.wikipedia.org/wiki/Ssh-keygen
# https://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html
