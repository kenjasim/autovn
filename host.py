from pathlib import Path
import subprocess
import re 
import os 
from network import Network


class Host(object): 

    def __init__(self, vmname, image):
        """
        Initialises Ubuntu Server 20.04 virtual machine via VirtualBox
        Options:
            label: user defined label to identify host 
            image: name of the .ova image located in vm_templates directory 
        """
        self.vmname = vmname
        self.image = image 
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
        ipath = Path(__file__).parent.absolute() / "vm_templates" / ("\"" + self.image + ".ova\"")
        cmd = 'VBoxManage import ' + str(ipath)
        subprocess.getoutput(cmd)
        # Rename the virtual machine
        cmd = 'vboxmanage modifyvm "' + self.image + '" --name ' + self.vmname
        subprocess.getoutput(cmd)
        # Check vm successfully imported 
        if not self.check_exists(self.vmname):
            raise Exception("[!] Failed to import virtual machine.")

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

    def delete_vm(self, vm):
        """
        Permanently delete the virtual machine and all it's files 
        """
        cmd = 'VBoxManage unregistervm --delete ' + self.vmname
        subprocess.getoutput(cmd)
        
    
################################################################################
# Main
################################################################################

if __name__ == '__main__':
    h = Host("hostA", "Ubuntu Server 20.04")
    h.assign_network(1, "vboxnet1")
    h.assign_network(2, "vboxnet2")
    h.assign_internet(1) 
    h.start() 

################################################################################
# Resources
################################################################################