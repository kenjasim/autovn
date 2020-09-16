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

    @classmethod
    def get_vmname(self, vmname):
        """Return a host with a given vmname"""
        host = Session.query(Host).filter_by(vmname=vmname).first()
        if host:
            return host
        else:
            return None

    @classmethod
    def check_database(self):
        """Check if db has any hosts"""
        host = Session.query(Host).first()
        if host:
            return host
        else:
            return None

    @classmethod
    def post(self, host):
        """Put a host into the database"""
        host.write_to_db()
    
    @classmethod
    def get_ip(self, vmname): 
        """Get the ip address of the host"""
        host = Session.query(Host).filter_by(vmname=vmname).first()
        if host:
            return host.get_ip()
