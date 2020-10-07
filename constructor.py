import yaml, pathlib, os
from models.network import Network
from models.host import Host
from models.deployment import Deployment

from print_colours import Print
from sqlalchemy.exc import OperationalError

from resources import Hosts, Networks, Deployments

class Constructor():

    def __init__(self, template_file):
        """
        Parse and return the hosts and networks from the template file.

        Keyword Arguments:
            template_file - The yaml template file to read
        """
        # Generate the network
        self.networks = {}
        self.hosts = {}

        # Build the path
        template_path = str(pathlib.Path(__file__).parent.absolute() / "templates" / template_file )

        # Check if the path exits
        if (os.path.isfile(template_path)):
            # Read the template file
            with open(template_path) as file:
                self.template = yaml.safe_load(file)
        else:
            raise Exception("Failed to find the file " + template_file)

    def parse(self):
        """
        Parse the network template.

        Returns:
            network - Dictionary of created networks
            hosts - dictionary of created hosts
        """
        # Read the network and host files
        deployment_name = self.create_deployment()

        self.build_networks(deployment_name)
        self.build_hosts(deployment_name)

        self.add_to_db()

    def create_deployment(self):
        """
        Initialise deployment for grouping host-network topologies. 
        """
        if "deployment" in self.template:
            name = self.template['deployment']['name']
            d = Deployment(name)
            Deployments().post(d)
            Print.print_information("Building deployment: " + name)
        return name

    def build_networks(self, deployment_name):
        """
        Reads the network information from the template 
        """
        # Read the network information and catch if it doesnt exist
        
        if "networks" in self.template:
            networks = self.template['networks']
            # Loop through the networks and collect the information
            for label, values in networks.items():
                # Validate template and network address 
                if self.is_valid_net_template(values) and self.is_valid_net_addr(values["netaddr"]): 
                    # Build the network 
                    deployment_id = Deployments.get_by_name(deployment_name).id
                    self.networks[label] = Network(label, values["netaddr"], values["dhcplower"], values["dhcpupper"], deployment_id)
                else: 
                    Print.print_error("Failed network template checks.")             
        else:
            raise Exception("No network information in template")

    def build_hosts(self, deployment_name):
        """
        Creates the host virtual machines from the template. 
        """
        # Read the hosts information and catch if it doesnt exist

        if "hosts" in self.template:
            hosts = self.template['hosts']

            # Loop through the hosts and collect the information
            for vmname, values in hosts.items():
                # Validate template and host name
                if self.is_valid_host_template(values) and self.is_valid_host_vname(vmname): 
                    
                    # Build the host
                    deployment_id = Deployments.get_by_name(deployment_name).id
                    self.hosts[vmname] = Host(vmname, values["image"], values["username"], values["password"], deployment_id)
                    
                    # Manage network assignments
                    networks = values["networks"]
                    # Assign the network access if that is required
                    if values["internet_access"]:
                        # Assign internet to the very first adapter 
                        networks.insert(0, "Internet")
                        self.hosts[vmname].assign_internet(1)
                    # Loop through rest of list and assign adapter
                    for index, networklabel in enumerate(networks):
                        # Check if its in the list and that the adapters havent gone over 8
                        if networklabel in networks and index + 1 < 8 and networklabel != "Internet":
                            self.hosts[vmname].assign_network(index+1, self.networks[networklabel].get_name())
                else: 
                    Print.print_error("Failed host template checks.")    
        else:
            Print.print_error("No host information in template")

    def is_valid_net_template(self, values): 
        """
        Check all values are present. 
        """ 
        if "netaddr" and "dhcplower" and "dhcpupper" in values:
            return True 
        return False

    def is_valid_net_addr(self, netaddr):
        """
        Check netaddr is unique.
        """
        if Networks.get_ipaddr(netaddr=netaddr): 
            return False
        return True

    def is_valid_host_template(self, values): 
        """
        Check all values are present. 
        """ 
        if "image" and "username" and "password" and "networks" and "internet_access" in values:
            return True 
        return False

    def is_valid_host_vname(self, vmname):
        """
        Check vmname is unique.
        """
        if Hosts.get_vmname(vmname=vmname): 
            return False
        return True

    def add_to_db(self):
        """
        Add the networks and hosts to the database
        """
        try:
            for network in self.networks.values():
                # Add network to db
                Networks().post(network)
            for host in self.hosts.values():
                # Destroy the hosts
                Hosts().post(host)
        except Exception as e:
            Print.print_error("Aborting import due to {0}".format(e))
        