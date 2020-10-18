from sqlalchemy import Column, Integer, String, ForeignKey
from db import Base
from db import Session
from secrets import token_urlsafe

class Token(Base):
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True)
    token = Column(String(80))
    user_id = Column(Integer, ForeignKey('users.id'))

    def __init__(self, user_id):
        self.token = token_urlsafe()
        self.user_id = user_id

    def write_to_db(self):
        """Save user to database"""
        Session.add(self)
        Session.commit()

    # def __repr__(self):
    #     return f"<User:: id: {self.id}, username: {self.username}>"


    # @classmethod
    # def find_by_id(cls, _id):
    #     """Return user instance from database record"""
    #     return cls.query.filter_by(id=_id).first()