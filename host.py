from pathlib import Path
import subprocess
import re
import os
import time
from network import Network
from tabulate import tabulate
from autossh import ssh_shell

class Host(object):

    def __init__(self, vmname, image, username, password):
        """
        Initialises Ubuntu Server 20.04 virtual machine via VirtualBox
        Options:
            label: user defined label to identify host
            image: name of the .ova image located in vm_templates directory
            username: username of the machine
            password: password of the machine
        """
        self.vmname = vmname
        self.image = image
        self.username = username
        self.password = password
        # Check if image template or vmname already exists
        if self.check_exists(image):
            raise Exception("[!] Template image already exists, unable to duplicate")
        if self.check_exists(vmname):
            raise Exception("[!] VM image with assigned name already exists")
        # Import image into VirtualBox
        self.import_image()

    @classmethod
    def check_exists(self, vmname):
        """Check if a virtual machine with the given label exists"""
        # Collate list of currently imported vm names
        cmd = ['vboxmanage list vms']
        vmsfound = re.findall(r"\"(.*)\"", subprocess.getoutput(cmd))
        # Check if any match
        for name in vmsfound:
            if vmname == name:
                return True

    def import_image(self):
        """
        Import vm .ova image into VirtualBox
        """
        # Form path to image
        cmd = 'VBoxManage import ' + str(Path("\"" + self.image + "\"")) + ' --vsys 0 --vmname ' + self.vmname
        subprocess.getoutput(cmd)

        # Check vm successfully imported
        if not self.check_exists(self.vmname):
            raise Exception("[!] Failed to import virtual machine.")
        else:
            print("\u001b[32;1m[✓] Successfully imported machine " + self.vmname + "\u001b[0m")

    def assign_network(self, adapter, netname):
        """
        Assign a virtual machine adapter to a network
        Options:
            adapter: Adapter of host to be used, e.g. 1 to 8
            netname: Name of the host-only network to connect to
        """
        # Check network exists
        if not Network.check_exists(netname):
            raise Exception("[!] Unable to assign network, does not exist.")
        # Set network interface type to host-only
        cmd = 'vboxmanage modifyvm ' + self.vmname + ' --nic' + str(adapter) + ' hostonly'
        subprocess.getoutput(cmd)
        # Assign network interface adapter to the host-only network
        cmd = 'vboxmanage modifyvm ' + self.vmname + ' --hostonlyadapter' + str(adapter) + ' ' + netname
        subprocess.getoutput(cmd)

    def assign_internet(self, adapter):
        """
        Assign a 'nat' interface to the virtual machines for internet
        access through the hosting machine.
        Options:
            adapter: Adapter of host to be used, e.g. 1 to 8
        """
        # Assign adapter to nat interface
        cmd = 'vboxmanage modifyvm ' + self.vmname + ' --nic' + str(adapter) + ' nat'
        subprocess.getoutput(cmd)

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
            if "hostonlyadapter" in key or "natnet" in key:
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
        """
        Return host username.
        """
        return self.username

    def start(self, headerless=True):
        """
        Start running virtual machine.
        Options:
            headerless: run without VirtualBox display (default is True)
        """
        # Set headerless option and start VM
        cmd = 'VBoxManage startvm ' + self.vmname
        if headerless:
            cmd += ' --type headless'
        r = subprocess.getoutput(cmd)
        # Check if successfull
        if "successfully started" not in r:
            raise Exception("[!] Failed to start virtual machine: " + r)

    def stop(self):
        """
        Shutdown the virtual machine.
        """
        cmd = 'VBoxManage controlvm ' + self.vmname + ' poweroff'
        subprocess.getoutput(cmd)

    def restart(self):
        """
        Power off and on again the virtual machine.
        """
        self.stop()
        self.start()

    def destroy(self):
        """
        Permanently delete the virtual machine and all it's files.
        """
        # Delete SSH known_hosts entry
        if self.get_ip():
            cmd = "sed -i '' '/" + self.get_ip() + "/d' ~/.ssh/known_hosts"
            subprocess.getoutput(cmd)
        # Delete virtual machine from VirtualBox
        cmd = 'VBoxManage unregistervm --delete ' + self.vmname
        subprocess.getoutput(cmd)

    def ssh(self):
        """
        Launch SSH session with host.
        """
        shell = ssh_shell.Shell()
        # Retrieve IP address
        ip = self.get_ip()
        if ip is None:
            raise Exception("[!] IP address not assigned.")
        # Open SSH session through new terminal
        shell.connect(hostname=self.username, hostaddr=ip, password=self.password)

    def dist_pkey(self):
        """
        Create and distribute SSH keys for/to the host.
        """
        keyname = "id_rsa_vb"
        ap = Path(__file__).parent.absolute() / "keys" / keyname
        # Check if key already exists
        if not ((os.path.isfile(str(ap))) or (os.path.isfile(str(ap) + ".pub"))):
            # Create RSA key pair
            cmd = "ssh-keygen -t rsa -b 4096 -q -N \"\" -f " + str(ap)
            s = subprocess.getoutput(cmd)
        if not ((os.path.isfile(str(ap))) or (os.path.isfile(str(ap) + ".pub"))):
            raise Exception("[!] RSA key pair generation failed.")
        # Add private key the SSH agent
        cmd = "eval `ssh-agent`"
        s = subprocess.getoutput(cmd)
        cmd = "ssh-add " + str(ap)
        s = subprocess.getoutput(cmd)
        # Share public key with host
        shell = ssh_shell.Shell()
        ip = self.get_ip()
        r = shell.copy(hostname=self.username, hostaddr=ip, password=self.password, keypath=(str(ap) + ".pub"))
        print(r)
        if "try logging" not in r:
            raise Exception("[!] Failed to distribute SSH public key to host.")

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


################################################################################
# Main
################################################################################

if __name__ == '__main__':
    h = Host("master", "vm_templates/Ubuntu Server 20.04.ova", "dev", "ved")
    h.assign_internet(1)
    h.assign_network(2, "vboxnet0")
    h.start()
    time.sleep(20)
    print(h)
    h.ssh()
    h.stop()
    h.destroy()



################################################################################
# Resources
################################################################################
# https://en.wikipedia.org/wiki/Ssh-keygen
# https://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html
