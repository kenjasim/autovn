import functools
from security import authorise 

def make_secure(access_level):
    def decorator(func):
        @functools.wraps(func)
        def secure_function(*args, **kwargs):
            user = args[0]
            for u in USERS:
                if u.username == user.username:
                    if authorise(username, token):
                        print("here")
                        return func(*args, **kwargs)
                    # else:
                    #     return f"No {access_level} permissions for {user['username']}."
        return secure_function
    return decorator


class User(object): 
    def _init_(self, access_level, username, password):
        self.access_level = access_level
        self.username = username
        self.password = password

auser = User("admin", "ken", "123")
USERS = [auser]

# def authenticate(user, access_level, password):
#     if user.access_level == access_level and user.password == password:
#         return True

@make_secure("admin")
def get_admin_password(user):
   print("admin: 1234")

get_admin_password(auser)