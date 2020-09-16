from models.host import Host
from db import Session

class Hosts():
    """
    Resource for dealing with requests to the database
    """

    @classmethod
    def get_all(self):
        """Return all hosts"""
        hosts = Session.query(Host).all()
        if hosts:
            return hosts
        raise Exception("No hosts in database")
