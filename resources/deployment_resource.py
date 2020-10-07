from models.deployment import Deployment
from db import Session

class Deployments():

    @classmethod
    def post(self, deployment):
        """Put a host into the database"""
        deployment.write_to_db()

    @staticmethod
    def get_last():
        """
        Get the last item into the database
        """
        d = Session.query(Deployment).order_by(Deployment.id.desc()).first()
        return d

    @staticmethod
    def delete_by_id(deployment_id):
        """Delete a deployment by id"""
        deployment = Session.query(Deployment).filter_by(id=deployment_id).first()
        if deployment:
            deployment.delete_from_db()

    @staticmethod
    def delete_by_name(name):
        """Delete a deployment by id"""
        deployment = Session.query(Deployment).filter_by(name=name).first()
        if deployment:
            deployment.delete_from_db()
    
    @staticmethod
    def get_by_name(name): 
        """Get the deployment matched by name"""
        deployment = Session.query(Deployment).filter_by(name=name).first()
        return deployment

    @staticmethod
    def get_by_id(deployment_id):
        """Get the deployment matched by id"""
        deployment = Session.query(Deployment).filter_by(id=deployment_id).first()
        return deployment
        