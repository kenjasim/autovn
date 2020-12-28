from models.token import Token
from db import Session

class Tokens():

    @staticmethod
    def post(user_id):
        """generate a token and add to the database"""
        token = Token(user_id)
        token.write_to_db()
        return token

    @staticmethod
    def get_by_token(token):
        return Session.query(Token).filter_by(token=token).first()
    
    @staticmethod 
    def get_by_user_id(user_id):
        return Session.query(Token).filter_by(user_id=user_id).all() 