from werkzeug.security import safe_str_cmp, generate_password_hash, check_password_hash
from resources import Users, Tokens
from db import Session
from print_colours import Print
from getpass import getpass
from datetime import datetime

def hash_password(password):
    """Returns a digest hash of a users password"""
    return generate_password_hash(password)

def check_password(user, password):
    """Returns true if users password is matched to account"""
    return check_password_hash(user.passhash, password)

def authenticate(username, password):
    """Returns a session token if the user and password is matched to an account"""
    user = Users.find_by_username(username)

    if user is None:
        raise Exception("User not in database")

    if check_password(user, password):
        # Check if existing token(s) and remove
        user_id = user.id 
        tokens = Tokens.get_by_user_id(user_id)
        for token in tokens: 
            Session.delete(token)
            Session.commit()
        # Generate new token
        token = Tokens.post(user.id)
        return token.token

def authorise(username, token):
    """Returns True if session token valid for user"""
    user = Users.find_by_username(username)
    if user is None:
        Print.print_error("User not in database")
        return

    token = Tokens.get_by_token(token)
    if token is None:
        Print.print_error("Token is not in the database")
        return 

    # Verify token matched to user
    if user.id != token.user_id:
        Print.print_error("Token not matched to user")
        return

    # Validate token deadline 
    dt = datetime.utcnow()
    if token.deadline < dt: 
        Session.delete(token)
        Session.commit()
        Print.print_error("Token has expired")
        return
     
    return True
        
def default_user():
    """Create admin user if no user in database"""
    users = Users.get_all()
    if users is None:
        Print.print_information("Creating admin user...")
        while True:
            password = getpass("Enter admin Password: ")
            password_check = getpass("Re-Enter admin Password: ")
            if password != password_check:
                Print.print_warning("Passwords dont match")
            else:
                break
        passhash = hash_password(password)
        Users.post("admin", passhash)

def change_password(username, old_pass, new_pass):
    """Change a users password"""
    # Get the user to update the password for
    user = Users.find_by_username(username)

    if user is None:
        raise Exception("User not in database")

    # Authorise request
    if not check_password(user, old_pass):
        Print.print_warning("Failed to authenticate")
    # Update password
    else:
        passhash = hash_password(new_pass)
        user.passhash = passhash
        user.update_to_db()

def remove_user(username, password):
    # Get the user
    user = Users.find_by_username(username)
    
    if user is None:
        raise Exception("User not in database")
    
    # Authorise request
    if not check_password(user, password):
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


