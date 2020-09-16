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
    def post(self, network):
        """Put a network into the database"""
        network.write_to_db()
