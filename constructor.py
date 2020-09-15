import yaml
from models.network import Network
from models.host import Host

from print_colours import Print
from models.db import Session
from sqlalchemy.exc import OperationalError
from models.db import create_tables

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
        self.groups = {}

        # Create SQL tables for networks and hosts 
        create_tables()

        # Read the template file
        with open(template_file) as file:
            self.template = yaml.safe_load(file) 

    def parse(self):
        """
        Parse the network template.

        Returns:
            network - Dictionary of created networks
            hosts - dictionary of created hosts
        """
        # Read the network and host files
        self.read_networks()
        self.read_hosts()

        # Return the lists
        return self.networks, self.hosts

    def read_networks(self):
        """
        Reads the network information from the template.
        """
        # Read the network information and catch if it doesnt exist

        if "networks" in self.template:
            networks = self.template['networks']

            # Loop through the networks and collect the information
            for label, values in networks.items():
                network = None
                # Check if host already exists in database 
                network = Session.query(Network).filter_by(label=label).first() 
                if network is not None:
                    self.networks[label] = network
                    Print.print_success("Successfully imported existing network " + label + "from the database")
                else:
                    # Else, create network 
                    if "netaddr" and "dhcplower" and "dhcpupper" in values:
                        self.networks[label] = Network(label, values["netaddr"], values["dhcplower"], values["dhcpupper"])
                        # Save network to the database 
                        Session.add(self.networks[label])
                        Session.commit() 
        else:
            raise Exception("No network information in template")

    def read_hosts(self):
        """
        Reads the network information from the template.
        """
        # Read the hosts information and catch if it doesnt exist

        if "hosts" in self.template:
            hosts = self.template['hosts']

            # Loop through the hosts and collect the information
            for vmname, values in hosts.items():
                host = None
                # Check if host already exists in database 
                host = Session.query(Host).filter_by(vmname=vmname).first() 
                if host is not None:
                    self.hosts[vmname] = host
                    Print.print_success("Successfully imported existing host " + vmname + "from the database")
                else:
                    # Else, create host 
                    if "image" and "username" and "password" and "networks" and "internet_access" in values:
                        self.hosts[vmname] = Host(vmname, values["image"], values["username"], values["password"])

                        # Manage network assignments 
                        networks = values["networks"]
                        # Assign the network access if that is required
                        if values["internet_access"]:
                            networks.insert(0, "Internet")
                            self.hosts[vmname].assign_internet(1)
                        # Loop through rest of list and assign adapter
                        for index, networklabel in enumerate(networks):
                            # Check if its in the list and that the adapters havent gone over 8
                            if networklabel in networks and index + 1 < 8 and networklabel != "Internet":
                                self.hosts[vmname].assign_network(index+1, self.networks[networklabel].get_name())
                        # Save hosts to the database 
                        Session.add(self.hosts[vmname])
                        Session.commit() 
        else:
            raise Exception("No host information in template")
