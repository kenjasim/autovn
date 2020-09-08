from pathlib import Path
import subprocess
import re 


class Network(object): 

    def __init__(self, netaddr, dhcplower, dhcpupper):
        """
        Initialises VirtualBox host-only network interface 
        Options:
            hostname: name of host only interface
            hostaddr: address of the interface
            dhcplower - Lower range of assignable ip addresses
            dhcpupper - Upper range of assignable ip addresses
        """
        self.netname = self.next_name() # recieve name from VirtualBox
        self.netaddr = netaddr
        self.dhcplower = dhcplower
        self.dhcpupper = dhcpupper
        # Call VirtualBox to create network 
        self.create_network() 

    @classmethod
    def check_exists(self, netname):
        """
        Check if network already exists.
        """
        r = subprocess.getoutput("vboxmanage list hostonlyifs|grep '" + netname + "'")
        if (r != ""):
            return True 
    
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
        bigid = netids[-1] # largest id assigned
        for n in range(0, bigid + 2): # search for smallest unused id, up to 1 greater than the largest  
            if n not in netids:
                return "vboxnet" + str(n) 
        raise Exception("[!] Failed to find a free network name.")

    def create_network(self):
        """
        Create host-only network interface. 
        Note, VirtualBox increments host-only names, e.g. "vboxnetN"
        """
        # Check if network name is avaliable 
        if self.check_exists(self.netname):
            raise Exception("[!] Network with name " + self.netname + " already exists.")
        # Create host-only network interface 
        subprocess.getoutput("VBoxManage hostonlyif create")
        # Check if network has been created 
        if not self.check_exists(self.netname):
            raise Exception("[!] Failed to create network with name " + self.netname)
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

    def destroy_network(self):
        """
        Permanently destroy host-only network. 
        """
        # Destroy DHCP server 
        cmd = 'VBoxManage dhcpserver remove --interface ' + self.netname
        subprocess.getoutput(cmd)
        # Delete DHCP logs and lease config files 
        # Linux config location ~/.config/VirtualBox/...
        # Mac config location ~/Library/VirtualBox
        path = Path.home().glob('Library' + '/VirtualBox' + '/HostInterfaceNetworking-' + self.netname + '-Dhcpd.*')
        for filepath in path:
            cmd = 'rm ' + str(filepath)
            subprocess.getoutput(cmd)
        # Destroy host-only network interface 
        cmd = 'VBoxManage hostonlyif remove ' + self.netname
        subprocess.getoutput(cmd)
        # Set network object properties to None (indicate deleted)
        self.netname = None
        self.netaddr = None
            

################################################################################
# Main
################################################################################

if __name__ == '__main__':
    n = Network("20.0.0.1", "20.0.0.2", "20.0.0.254") 


################################################################################
# Resources
################################################################################