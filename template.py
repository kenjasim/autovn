import yaml
from models.network import Network
from models.host import Host

class Template():

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
            for network, values in networks.items():
                if "netaddr" and "dhcplower" and "dhcpupper" in values:
                    self.networks[network] = Network(values["netaddr"], values["dhcplower"], values["dhcpupper"])
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
            for host, values in hosts.items():
                if "image" and "username" and "password" and "networks" and "internet_access" in values:
                    self.hosts[host] = Host(host, values["image"], values["username"], values["password"])

                    # Manage network assignments 
                    networks = values["networks"]
                    # Assign the network access if that is required
                    if values["internet_access"]:
                        networks.insert(0, "Internet")
                        self.hosts[host].assign_internet(1)
                    # Loop through rest of list and assign adapter
                    for index, network in enumerate(networks):
                        # Check if its in the list and that the addapters havent gone over 8
                        if network in networks and index + 1 < 8 and network != "Internet":
                            self.hosts[host].assign_network(index+1, self.networks[network].get_name())
        else:
            raise Exception("No host information in template")
