from models.host import Host
from db import Session
import json

class Hosts():
    """
    Resource for dealing with requests to the database
    """

    @classmethod
    def get_all(self):
        """Return all hosts"""
        hosts = Session.query(Host).all()
        if hosts:
            host_list = []
            for host in hosts:
                h_dict = host.dict()
                host_list.append(h_dict)
            return json.dumps(host_list)
        raise Exception("No hosts in database")
