import yaml, pathlib, os
from models.network import Network
from models.host import Host
from models.deployment import Deployment
import logging

from print_colours import Print
from sqlalchemy.exc import OperationalError

from resources import Hosts, Networks, Deployments

class Constructor():
    """Collection of methods to build the topology from a configuration file."""

    def __init__(self, template_file):
        """
        Parse and return the hosts and networks from the template file.
        Options:
            template_file (str): The name of the yaml configuration template file
        """
        # Generate the network
        self.networks = {}
        self.hosts = {}

        # Build the path
        template_path = str(pathlib.Path().home() / ".avn" / "templates" / template_file )

        # Check if the path exits
        if (os.path.isfile(template_path)):
            # Read the template file
            with open(template_path) as file:
                self.template = yaml.safe_load(file)
        else:
            raise Exception("Failed to find the file " + template_file)

    def parse(self):
        """
        Parse the network template to build hosts and networks.
        """
        deployment_name = None
        # Read the network and host files
        try:
            deployment_name = self.create_deployment()
            self.build_networks(deployment_name)
            self.build_hosts(deployment_name)
            self.add_to_db()
        except Exception as e:
            Print.print_error("Build aborted with reason: {0}".format(e))
            Print.print_information("Cleaning build...")

            # Clear up any built networks
            self.clear_up_networks()

            # Clear up any built VMs
            self.clear_up_hosts()

            # Clear the deployment from the db
            if deployment_name:
                Print.print_information("Cleaning database...")
                self.clear_up_database(deployment_name)
            
    def create_deployment(self):
        """Initialise deployment for grouping host-network topologies."""
        if "deployment" in self.template:
            name = self.template['deployment']['name']

            #Check if the name is unique (not already in db)
            if self.is_valid_deployment_name(name):
                d = Deployment(name)
                Deployments().post(d)
                Print.print_information("Building deployment: " + name)
                return name

    def build_networks(self, deployment_name):
        """Build networks inline with configuration template."""
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
            raise Exception("No network information in template")

    def build_hosts(self, deployment_name):
        """Build networks inline with configuration template."""
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
                    # Initiaise adapter identifier, starts at adapter 1
                    adapter = 1
                    # Loop through rest of list and assign adapter
                    for index, networklabel in enumerate(networks):
                        adapter += index # at first iteration index = 0
                        # Check if network has been created and adapters havent gone over 8
                        if networklabel in self.networks and adapter <= 8:
                            self.hosts[vmname].assign_network(adapter, self.networks[networklabel].get_name())
                        else:
                            raise Exception("Error assigning network adapter, please check template file")
                    # Point to next free adapter 
                    adapter += 1
                    # Assign network access if required to the next adapter
                    if "internet_adapter" in values:
                        # Check a free adapter is avaliable 
                        if adapter <= 8:
                            try:
                                self.hosts[vmname].assign_internet(adapter, values["internet_adapter"])
                            except Exception as e:
                                raise Exception("failed to assign internet adapter: " + repr(e)) 
                        else:
                            raise Exception("Error adapter count for host exceeded")
        else:
            Print.print_error("No host information in template")

    def is_valid_deployment_name(self, deployment_name):
        """Check if the deployment name is in the database, if present raise an exception."""
        if Deployments.get_by_name(deployment_name) == None:
            return True
        raise Exception("Deployment name {0} is already in use".format(deployment_name))
        
    def is_valid_net_template(self, values): 
        """Check all required key-values are present in the networks template section.""" 
        if "netaddr" and "dhcplower" and "dhcpupper" in values:
            return True 
        raise Exception("Network template invalid. Please ensure all fields are present")

    def is_valid_net_addr(self, netaddr):
        """Check netaddr is unique."""
        if Networks.get_ipaddr(netaddr=netaddr) == None: 
            return True
        raise Exception("Network address already used. Please change in template")

    def is_valid_host_template(self, values): 
        """Check all required key-values are present in the hosts template section.""" 
        if "image" and "username" and "password" and "networks" in values:
            return True 
        raise Exception("Host template invalid. Please ensure all fields are present")

    def is_valid_host_vname(self, vmname):
        """Check vmname is unique."""
        if Hosts.get_vmname(vmname=vmname) == None: 
            return True
        raise Exception("Virtual machine name already used. Please change in template")

    def clear_up_networks(self):
        """Clear from virtualbox any networks built during constructor phase."""
        for network in self.networks.values():
            network.destroy()

    def clear_up_hosts(self):
        """Clear from virtualbox any hosts built during constructor phase."""
        for host in self.hosts.values():
            host.destroy()

    def clear_up_database(self, deployment_name):
        """Clear any built networks and hosts during the constructor phase."""
        # Get any networks writen to the database
        networks = Networks().get_deployment_by_name(deployment_name)
        # Remove from database
        if networks:
            for network in networks:
                Networks().delete(network)
        # Get any hosts writen to the database
        hosts = Hosts().get_deployment_by_name(deployment_name)
        # Remove from database
        if hosts:
            for host in hosts:
                Hosts().delete(host)
        # Remove Deployment
        Deployments().delete_by_name(deployment_name)

    def add_to_db(self):
        """Add the networks and hosts to the database."""
        for network in self.networks.values():
            # Add network to db
            Networks().post(network)
        for host in self.hosts.values():
            # Destroy the hosts
            Hosts().post(host)
        