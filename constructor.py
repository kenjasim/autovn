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
        self.create_deployment()

        self.read_networks()
        self.read_hosts()

        self.add_to_db()

    def create_deployment(self):
        d = Deployment()
        Deployments().post(d)
        Print.print_information("Building deployment with id {0}".format(Deployments().get_last().id))

    def read_networks(self):
        """
        Reads the network information from the template.
        """
        # Read the network information and catch if it doesnt exist

        
        if "networks" in self.template:
            networks = self.template['networks']

            try:
                # Loop through the networks and collect the information
                for label, values in networks.items():
                    # Else, create network
                    if "netaddr" and "dhcplower" and "dhcpupper" in values:
                        d = Deployments.get_last()
                        self.networks[label] = Network(label, values["netaddr"], values["dhcplower"], values["dhcpupper"], d.id)
            except Exception as e:
                Print.print_error("Aborting import due to {0}".format(e))
                Print.print_information("Performing cleanup...")
                self.clean_up()
        else:
            raise Exception("No network information in template")

    def read_hosts(self):
        """
        Reads the network information from the template.
        """
        # Read the hosts information and catch if it doesnt exist

        if "hosts" in self.template:
            hosts = self.template['hosts']

            try:
                # Loop through the hosts and collect the information
                for vmname, values in hosts.items():
                    # Else, create host
                    
                        if "image" and "username" and "password" and "networks" and "internet_access" in values:
                            d = Deployments.get_last()
                            self.hosts[vmname] = Host(vmname, values["image"], values["username"], values["password"], d.id)

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
            except Exception as e:
                Print.print_error("Aborting import due to {0}".format(e))
                Print.print_information("Performing cleanup...")
                self.clean_up()
        else:
            Print.print_error("No host information in template")

    def clean_up(self):
        """
        If there is an error in importing then clean up any created objects
        """    
        for network in self.networks.values():
            # Destroy the network
            network.destroy()
        
        for host in self.hosts.values():
            # Destroy the hosts
            host.destroy()

        deployment_id = Deployments().get_last().id

        networks = Networks().get_deployment(deployment_id)
        if networks:
            # Delete host database entry
            for network in networks:
                Networks().delete(network)


        hosts = Hosts().get_deployment(deployment_id)
        if hosts:
            # Delete host database entry
            for host in hosts:
                Hosts().delete(host)

        # Delete deployment
        Deployments().delete_by_id(Deployments().get_last().id)

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
            Print.print_information("Performing cleanup...")
            self.clean_up()
        