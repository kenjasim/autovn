from werkzeug.security import safe_str_cmp
from resources import Users, Tokens
from db import Session
from print_colours import Print
from getpass import getpass


def authenticate(username, password):
    user = Users.find_by_username(username)
    if user and safe_str_cmp(user.password, password):
        # Check if existing token 
        user_id = user.id 
        tokens = Tokens.get_by_user_id(user_id)
        for token in tokens: 
            Session.delete(token)
            Session.commit()
        token = Tokens.post(user.id)
        return token.token

def authorise(username, token):
    user = Users.find_by_username(username)
    token = Tokens.get_by_token(token)
    if user and token and user.id == token.user_id:
        return True
    else:
        return False

def default_user():
    """Create admin user if no user in database"""
    users = Users.get_all()
    if users is None:
        Print.print_information("Creating admin user...")
        password = getpass("Enter admin Password: ")
        password_check = getpass("Re-Enter admin Password: ")
        if password != password_check:
            Print.print_warning("Passwords dont match")
        else:
            Users.post("admin", password)

def change_password(username, old_pass, new_pass):
    """Change a users password"""
    # Get the user to update the password for
    user = Users.find_by_username(username)

    if user is None:
        raise Exception("User not in database")

    # Do some checks
    if not safe_str_cmp(user.password, old_pass):
        Print.print_warning("Failed to authenticate")
    else:
        user.password = new_pass
        user.update_to_db()

def remove_user(username, password):
    # Get the user
    user = Users.find_by_username(username)
    
    if user is None:
        raise Exception("User not in database")
    
    # Do some checks
    if not safe_str_cmp(user.password, password):
        Print.print_warning("Failed to authenticate")

    else:
        # Delete any tokens
        user_id = user.id 
        tokens = Tokens.get_by_user_id(user_id)
        for token in tokens: 
            Session.delete(token)
            Session.commit()
        
        # delete user
        Session.delete(user)
        Session.commit()


