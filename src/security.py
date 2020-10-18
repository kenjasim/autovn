from werkzeug.security import safe_str_cmp
from resources import Users, Tokens


def authenticate(username, password):
    user = Users.find_by_username(username)
    if user and safe_str_cmp(user.password, password):
        token = Tokens.post(user.id)
        return token.token

def authorise(username, token):
    user = Users.find_by_username(username)
    token = Tokens.get_by_token(token)
    if user and token and user.id == token.user_id:
        return True
    else:
        return False