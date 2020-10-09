from models.port_forward import PortForward
from db import Session

class SSHForward():

    @staticmethod
    def get_all():
        """Return all sshforward servers in db"""
        sshforwards = Session.query(PortForward).all()
        return sshforwards

    @staticmethod
    def delete(sshforward):
        """Delete a sshforward from the database"""
        Session.delete(sshforward)
        Session.commit()