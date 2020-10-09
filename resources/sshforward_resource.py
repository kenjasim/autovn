from models.port_forward import PortForward
from models.deployment import Deployment
from db import Session

class SSHForward():

    @staticmethod
    def get_all():
        """Return all sshforward servers in db"""
        sshforwards = Session.query(PortForward).all()
        return sshforwards

    @staticmethod
    def get_by_deployment(deployment_name):
        """Return all sshforward servers in db"""
        deployment = Session.query(Deployment).filter_by(name=deployment_name).first()
        if deployment:
            sshforwards = Session.query(PortForward).filter_by(deployment_id= deployment.id).all()
            return sshforwards

    @staticmethod
    def delete(sshforward):
        """Delete a sshforward from the database"""
        Session.delete(sshforward)
        Session.commit()
