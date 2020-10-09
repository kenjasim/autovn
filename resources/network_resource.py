from models.network import Network
from models.deployment import Deployment
from db import Session

class Networks():
    """Collection of methods for reading/writing to Networks table of database."""

    @classmethod
    def get_all(self):
        """Return all networks."""
        networks = Session.query(Network).all()
        if networks:
            return networks
        raise Exception("No networks in database")
    
    @classmethod
    def get_ipaddr(self, netaddr):
        """Return networks with given ip address."""
        network = Session.query(Network).filter_by(netaddr=netaddr).first() 
        if network:
            return network

    @classmethod
    def get_deployment(self, deployment_id):
        """Return all hosts with a fiven deployment id."""
        networks = Session.query(Network).filter_by(deployment_id=deployment_id).all()
        if networks:
            return networks
        else:
            return None

    @classmethod
    def get_deployment_by_name(self, deployment_name):
        """Return all hosts with a fiven deployment id."""
        deployment = Session.query(Deployment).filter_by(name=deployment_name).first()
        if deployment:
            networks = Session.query(Network).filter_by(deployment_id=deployment.id).all()
            if networks:
                return networks

    @classmethod
    def post(self, network):
        """Put a network into the database."""
        network.write_to_db()

    @classmethod
    def delete(self, network):
        """Put a network into the database."""
        Session.delete(network)
        Session.commit()