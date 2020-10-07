from models.network import Network
from db import Session

class Networks():
    """
    Resource for dealing with requests to the database
    """

    @classmethod
    def get_all(self):
        """Return all networks"""
        networks = Session.query(Network).all()
        if networks:
            return networks
        raise Exception("No networks in database")

    @classmethod
    def get_deployment(self, deployment_id):
        """Return all hosts with a fiven deployment id"""
        networks = Session.query(Network).filter_by(deployment_id=deployment_id).all()
        if networks:
            return networks
        else:
            return None

    @classmethod
    def post(self, network):
        """Put a network into the database"""
        network.write_to_db()

    @classmethod
    def delete(self, network):
        """Put a network into the database"""
        Session.delete(network)
        Session.commit()