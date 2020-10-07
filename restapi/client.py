#!/usr/bin/python3

import requests
from pathlib import Path

class RESTClient(object): 
    """
    Client controller for deploying network on AVN.  
    """
    server_url = "http://127.0.0.1:5000/"

    @staticmethod
    def set_server_url(url):
        """
        Set url address for remote AVN server.
        Default: "http://127.0.0.1:5000/"
        """
        RESTClient.server_url = url

    @staticmethod
    def build(template_file="default.yaml"): 
        """
        Request AVN Rest API to build master-worker topology. 
        """
        url = RESTClient.server_url + "build/" + template_file
        r = requests.put(url)
        if r.status_code != 202:
            raise Exception("Failed to deploy topology: " + r.text)
    
    @staticmethod
    def start(deployment_name): 
        """
        Request AVN Rest API to start virtual host machines.  
        """
        url = RESTClient.server_url + "start/" + deployment_name
        r = requests.put(url)
        if r.status_code != 202:
            raise Exception("Failed to start topology: " + r.text)
    
    @staticmethod
    def restart(deployment_name): 
        """
        Request AVN Rest API to restart virtual host machines.  
        """
        url = RESTClient.server_url + "restart/" + deployment_name 
        r = requests.put(url)
        if r.status_code != 202:
            raise Exception("Failed to start topology: " + r.text)
    
    @staticmethod
    def send_keys(deployment_name): 
        """
        Request AVN Rest API to generate and distribute SSH keys.  
        """
        url = RESTClient.server_url + "keys/" + deployment_name
        r = requests.put(url)
        if r.status_code != 202:
            raise Exception("Failed to distribute keys: " + r.text)
    
    @staticmethod
    def destroy(deployment_name): 
        """
        Request AVN Rest API to destroy the topology. 
        """
        url = RESTClient.server_url + "destroy/" + deployment_name
        r = requests.delete(url)
        if r.status_code != 202:
            raise Exception("Failed to destroy topology: " + r.text)
    
    @staticmethod
    def host_details(): 
        """
        Request AVN Rest API to get host details
        Returns: dict
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
        Returns: dict
        """
        url = RESTClient.server_url + "details/networks"
        r = requests.get(url)
        if r.status_code != 200:
            raise Exception("Failed to GET network details: " + r.text)
        data = r.json() 
        return data 
    
    @staticmethod
    def get_hosts(): 
        """
        Request AVN Rest API to return hosts.
        Returns: dict
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
        Returns: dict
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
        Returns: dict
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


    

# HEADERS = {"Content-Type": "application/json",
#                     "Accept": "*/*",
#                     "Accept-Encoding": "gzip, deflate, br",
#                     "Connection": "keep-alive"}
    

