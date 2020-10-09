from sqlalchemy import Column, Integer, String, Sequence
from sqlalchemy.orm import relationship
from db import Base
from db import Session

class Deployment(Base):
    """
    Deployment object used to group related Network and Host objects.
    """
    # Define 'deployments' SQL table for instances of Deployment
    __tablename__ = 'deployments'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    hosts = relationship("Host")
    networks = relationship("Network")

    def __init__(self, name):
        self.name = name

    def write_to_db(self):
        """Write the host to the database"""
        Session.add(self)
        Session.commit()

    def delete_from_db(self):
        """Remove host from the database"""
        Session.delete(self)
        Session.commit()
