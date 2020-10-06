from sqlalchemy import Column, Integer, String, Sequence
from sqlalchemy.orm import relationship
from db import Base
from db import Session

class Deployment(Base):
    # Define the SQL alchemy model
    __tablename__ = 'deployment'
    id = Column(Integer, primary_key=True)
    hosts = relationship("Host")
    networks = relationship("Network")

    def write_to_db(self):
        """
        Write the host to the database
        """
        Session.add(self)
        Session.commit()

    def delete_from_db(self):
        """
        Remove host from the database
        """
        Session.delete(self)
        Session.commit()
