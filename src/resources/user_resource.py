from models.user import User
from db import Session
from getpass import getpass

class Users():

    @staticmethod
    def post(username, passhash):
        """add the user to the database"""
        username_exists = Session.query(User).filter_by(username=username).first()
        if username_exists:
            raise Exception("Username already taken")

        user = User(username, passhash)
        user.write_to_db()

    @staticmethod
    def get_all():
        """get all users in the database"""
        users = Session.query(User).all()
        user_list = []
        if users:
            for user in users:
                user_list.append(user.dict())
            return user_list
        else:
            return 

    @staticmethod
    def remove_user(username):
        """get all users in the database"""
        username_exists = Session.query(User).filter_by(username=username).first()
        if username_exists:
            Session.delete(username_exists)
            Session.commit()
            return
        
        raise Exception("Username {0} not in database".format(username))
    
    @staticmethod
    def find_by_username(username):
        """Return user instance from database record"""
        return Session.query(User).filter_by(username=username).first()

    @staticmethod
    def find_by_id(_id):
        """Return user instance from database record"""
        return Session.query(User).filter_by(id=_id).first()
    
