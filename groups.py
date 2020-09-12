from pathlib import Path
import xml.etree.ElementTree as ET
import subprocess


class Group(object):

    def __init__(self, name, **kwargs):
        """
        Defines a group for automating ansible configuration 
        deployment to hosts
        Options:
            name: name of the group 
            hosts: list of host members 
            **kwargs: group properties for configuration 
        """
        self.name = name 
        self.hosts = []
        if "hostname" in kwargs.keys():
            self.hostname = kwargs["hostname"]     

    def add_host(self, host): 
        """
        Add a host to the group. 
        """
        self.hosts.append(host) 

    def create_ansible_role(self): 
        """
        Generate the ansible role directory and YAML config file.
        """
        # ansiblePath = Path(__file__).parent.absolute() / 'ansible'
        # # Update ansible hosts file 
        # if not Path.is_file(str(ansiblePath / 'hosts')):
        #     print("can't find it :(")
        #     with open(str(ansiblePath / 'hosts'), 'w'): pass 
        # if not Path.is_file(str(ansiblePath / 'hosts')):
        #     raise Exception("[!] Unable to write to ansible host file")
        # with open(str(ansiblePath / 'hosts'), "a") as hosts:
        #     hosts.write("[" + self.name + "]\n")
        #     for host in self.hosts:
        #         hosts.write(host.get_ip() + " ansible_user=" + host.get_username())
        #     hosts.write("\n")
        # Create directory tree structure /roles/<groupname>/tasks/main.yaml 

        # Populate main.yaml config file with tasks 

    
    def __str__(self): 
        s = self.name
        if self.hostname:
            s += "\n Hostname: " + self.hostname
        s += "\n Hosts:"
        for host in self.hosts:
            s += "\n- " + host.vmname
        return s

################################################################################
# Main
################################################################################


################################################################################
# Resources
################################################################################
