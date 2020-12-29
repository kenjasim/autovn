from models.host import Host
from models.deployment import Deployment
from db import Session

class Hosts():
    """Collection of methods for reading/writing to Hosts table of database."""

    @classmethod
    def get_all(self):
        """Return all hosts."""
        hosts = Session.query(Host).all()
        if hosts:
            return hosts
        raise Exception("No hosts in database")

    @classmethod
    def get_deployment(self, deployment_id):
        """Return all hosts with a fiven deployment id."""
        hosts = Session.query(Host).filter_by(deployment_id=deployment_id).all()
        if hosts:
            return hosts
        else:
            return None

    @classmethod
    def get_deployment_by_name(self, deployment_name):
        """Return all hosts with a fiven deployment id."""
        deployment = Session.query(Deployment).filter_by(name=deployment_name).first()
        if deployment:
            hosts = Session.query(Host).filter_by(deployment_id=deployment.id).all()
            if hosts:
                return hosts

    @classmethod
    def get_vmname(self, vmname):
        """Return a host with a given vmname."""
        host = Session.query(Host).filter_by(vmname=vmname).first()
        if host:
            return host
        else:
            return None

    @classmethod
    def check_database(self):
        """Check if db has any hosts."""
        host = Session.query(Host).first()
        if host:
            return host
        else:
            return None

    @classmethod
    def post(self, host):
        """Put a host into the database."""
        host.write_to_db()
    
    @classmethod
    def get_ip(self, vmname): 
        """Get the ip address of the host."""
        host = Session.query(Host).filter_by(vmname=vmname).first()
        if host:
            return host.get_ip()

    @classmethod
    def get_ssh_remote_port(self, vmname): 
        """Get the ssh_remote_port of the host."""
        host = Session.query(Host).filter_by(vmname=vmname).first()
        if host:
            return host.get_ssh_remote_port() 

    @classmethod
    def delete(self, host):
        """Delete a host from the database."""
        Session.delete(host)
        Session.commit()
