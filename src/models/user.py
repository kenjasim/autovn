from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db import Base
from db import Session

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80))
    password = Column(String(80))
    token = relationship("Token")

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def write_to_db(self):
        """Save user to database"""
        Session.add(self)
        Session.commit()
    
    def dict(self):
        """Return an ordered dictionary for printing purposes."""
        # Get the dict and organised keys
        dict = self.__dict__
        keys = ["id", "username"]

        # Create and return a new dictionary
        new_dict= {}
        for key in keys:
            new_dict[key] = dict[key]
        return new_dict

    # def __repr__(self):
    #     return f"<User:: id: {self.id}, username: {self.username}>"


    # @classmethod
    # def find_by_id(cls, _id):
    #     """Return user instance from database record"""
    #     return cls.query.filter_by(id=_id).first()