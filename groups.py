from pathlib import Path
import xml.etree.ElementTree as ET
import subprocess
import os 


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
        ansiblePath = Path(__file__).parent.absolute() / 'ansible'
        # Update ansible hosts file 
        print(str(ansiblePath))
        if not os.path.isfile(str(ansiblePath / 'hosts')):
            print("can't find it :(")
            with open(str(ansiblePath / 'hosts'), 'w'): pass 
        if not os.path.isfile(str(ansiblePath / 'hosts')):
            raise Exception("[!] Unable to write to ansible host file")
        with open(str(ansiblePath / 'hosts'), "a") as hosts:
            hosts.write("[" + self.name + "]\n")
            for host in self.hosts:
                if not host.get_ip():
                    raise Exception("[!] Host has not been assigned and IP for ansible config.")
                hosts.write(host.get_ip() + " ansible_user=" + host.get_username())
            hosts.write("\n\n")
        # Create directory tree structure /roles/<groupname>/tasks/main.yaml 
        p = ansiblePath / 'roles'
        if not os.path.isdir(str(p)):
            os.mkdir(str(p))
        p = p / self.name
        if not os.path.isdir(str(p)):
            os.mkdir(str(p))
        p = p / 'tasks'
        if not os.path.isdir(str(p)):
            os.mkdir(str(p))
        # Create main.yaml config file
        p = p / 'main.yaml'
        if not os.path.isfile(str(p)):
            with open(str(p), 'w'): pass 
        # Populate main.yaml config file with tasks 
        with open(str(p), "a") as f:
            # Add tasks 
            if self.hostname:
                f.write("- name: change hostname to " + self.hostname + "\n")
                f.write("  hostname:" + "\n")
                f.write("    name: " + self.hostname + "\n") 
    
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
