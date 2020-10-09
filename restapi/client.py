#!/usr/bin/python3

import requests
from pathlib import Path
from autossh import ssh_shell

class RESTClient(object): 
    """Client controller for deploying network on AVN."""
    server_url = "http://127.0.0.1:5000/"

    @staticmethod
    def set_server_url(url):
        """
        Set url address for remote AVN server.
        Options:
            url (str): defaults to "http://127.0.0.1:5000/"
        """
        RESTClient.server_url = url

    @staticmethod
    def build(template_file="default.yaml"): 
        """
        Request AVN Rest API to build topology from configuration template file.
        Options:
            template_file (str): <template_name.yaml>
        """
        url = RESTClient.server_url + "build/" + template_file
        r = requests.put(url)
        if r.status_code != 202:
            raise Exception("Failed to deploy topology: " + r.text)
    
    @staticmethod
    def start(deployment_name): 
        """Request AVN Rest API to start virtual host machines."""
        url = RESTClient.server_url + "start/" + deployment_name
        r = requests.put(url)
        if r.status_code != 202:
            raise Exception("Failed to start topology: " + r.text)

    @staticmethod
    def stop(deployment_name): 
        """Request AVN Rest API to stop virtual host machines."""
        url = RESTClient.server_url + "stop/" + deployment_name
        r = requests.put(url)
        if r.status_code != 202:
            raise Exception("Failed to stop topology: " + r.text)
    
    @staticmethod
    def restart(deployment_name): 
        """Request AVN Rest API to restart virtual host machines."""
        url = RESTClient.server_url + "restart/" + deployment_name 
        r = requests.put(url)
        if r.status_code != 202:
            raise Exception("Failed to start topology: " + r.text)
    
    @staticmethod
    def send_keys(deployment_name): 
        """Request AVN Rest API to generate and distribute SSH keys."""
        url = RESTClient.server_url + "keys/" + deployment_name
        r = requests.put(url)
        if r.status_code != 202:
            raise Exception("Failed to distribute keys: " + r.text)
    
    @staticmethod
    def destroy(deployment_name): 
        """Request AVN Rest API to destroy the topology."""
        url = RESTClient.server_url + "destroy/" + deployment_name
        r = requests.delete(url)
        if r.status_code != 202:
            raise Exception("Failed to destroy topology: " + r.text)
    
    @staticmethod
    def host_details(): 
        """
        Request AVN Rest API to get host details
        Returns: 
            host_data (dict): {vmname: , VMState: , ostype: , cpus: , memory: , deployment: ,}
        """
        url = RESTClient.server_url + "details/hosts"
        r = requests.get(url)
        if r.status_code != 200:
            raise Exception("Failed to GET host details: " + r.text)
        data = r.json() 
        return data 

    @staticmethod
    def network_details(): 
        """
        Request AVN Rest API to get network details
        Returns:
            network_data (dict): {vmname: , name: , netname: , mac: , ip: , deployment: }
        """
        url = RESTClient.server_url + "details/networks"
        r = requests.get(url)
        if r.status_code != 200:
            raise Exception("Failed to GET network details: " + r.text)
        data = r.json() 
        return data 

    @staticmethod
    def shell(options):
        """
        Create an SSH shell terminal sessions with each host.
        Support for Mac and Linux (Gnome zsh). 
        Options:
            vmname      (str): name of rm to create shell session for
            server_ip   (str): ip address of the host machine 
            username    (str): virtual host's username 
            password    (str): virtual host's password
        """
        # Get the ssh_remote_port of the virtual machine
        port = None
        url = RESTClient.server_url + "host/" + options[0] + "/ssh_port"
        r = requests.get(url)
        if r.status_code != 200:
            raise Exception("Failed to GET ssh_remote_port: " + r.text)
        for data in r.json(): 
            if "port" not in data.keys():
                raise Exception("Failed to GET ssh_remote_port2: " + r.text)
            else:
                port = data["port"]
        # Open SSH session through new terminal
        shell = ssh_shell.Shell()
        shell.connect(hostname=options[2], hostaddr=options[1], password=options[3], hostport=port)

    @staticmethod
    def start_ssh_forwarder(deployment_name):
        """Start ssh forwarder server for connection to vm through host machine."""
        url = RESTClient.server_url + "sshforward/" + deployment_name
        r = requests.put(url)
        if r.status_code != 200:
            raise Exception("Failed to start SSH server: " + r.text)

    @staticmethod
    def stop_ssh_forwarders(deployment_name):
        """Stop ssh forwarder server for all hosts within deployment."""
        url = RESTClient.server_url + "stopsshforwarding/" + deployment_name
        r = requests.delete(url)
        if r.status_code != 200:
            raise Exception("Failed to start SSH server: " + r.text)
    
    @staticmethod
    def get_hosts(): 
        """
        Request AVN Rest API to return hosts.
        Returns:
            hosts (dict): {hostname: , username: , password: , image_name: }
        """
        url = RESTClient.server_url + "hosts"
        r = requests.get(url)
        if r.status_code != 200:
            raise Exception("Failed to GET hosts: " + r.text)
        data = r.json() 
        return data 
    
    @staticmethod
    def get_networks(): 
        """
        Request AVN Rest API to return networks.
        Returns:
            networks (dict): {label: , netname: , netaddr: , dhcplower: , dhcpupper: }
        """
        url = RESTClient.server_url + "networks"
        r = requests.get(url)
        if r.status_code != 200:
            raise Exception("Failed to GET networks: " + r.text)
        data = r.json() 
        return data 

    @staticmethod
    def get_ip(vmname): 
        """
        Request AVN Rest API to return the IP address for given vm-host.
        Returns:
            vm_ip (dict): {vmname: ip} 
        """
        url = RESTClient.server_url + "host/" + vmname + "ipv4" 
        r = requests.get(url)
        if r.status_code != 200:
            raise Exception("Failed to GET IP for host: " + r.text)
        data = r.json() 
        return data 
    
    @staticmethod
    def check_link():
        """
        Check connection to API Server. 
        """
        r = requests.get(RESTClient.server_url)
        if r.status_code != 200:
            raise Exception("Failed to GET IP for host: " + r.text) 
        return True
