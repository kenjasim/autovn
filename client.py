#!/usr/bin/python3

import requests
from pathlib import Path

AVNURL = "http://127.0.0.1:5000/"
HEADERS = {"Content-Type": "application/json",
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive"}

class AVNClient(object): 
    """
    Client controller for deploying network on AVN.  
    """

    @staticmethod
    def build(): 
        """
        Request AVN Rest API to build master-worker topology. 
        """
        template_name = "default.yaml"
        url = AVNURL + "build/" + template_name
        r = requests.put(url)
        if r.status_code != 202:
            raise Exception("Failed to deploy topology: " + r.text)
    
    @staticmethod
    def start(): 
        """
        Request AVN Rest API to start virtual host machines.  
        """
        url = AVNURL + "start"
        r = requests.put(url)
        if r.status_code != 202:
            raise Exception("Failed to start topology: " + r.text)
    
    @staticmethod
    def keys(): 
        """
        Request AVN Rest API to generate and distribute SSH keys.  
        """
        url = AVNURL + "keys"
        r = requests.put(url)
        if r.status_code != 202:
            raise Exception("Failed to distribute keys: " + r.text)
    
    @staticmethod
    def destroy(): 
        """
        Request AVN Rest API to destroy the topology. 
        """
        url = AVNURL + "delete"
        r = requests.delete(url)
        if r.status_code != 202:
            raise Exception("Failed to destroy topology: " + r.text)
    
    @staticmethod
    def host_details(): 
        """
        Request AVN Rest API to get host details
        Returns: dict
        """
        url = AVNURL + "details/hosts"
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
        url = AVNURL + "details/networks"
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
        url = AVNURL + "hosts"
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
        url = AVNURL + "networks"
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
        url = AVNURL + "host/" + vmname + "ipv4" 
        r = requests.get(url)
        if r.status_code != 200:
            raise Exception("Failed to GET IP for host: " + r.text)
        data = r.json() 
        return data 
    

    
    

