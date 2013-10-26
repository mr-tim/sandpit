from flask import redirect
from functools import wraps

from core import current_user

def logged_in(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        if current_user == None:
            return redirect('/login')
        else:
            return f(*args, **kwds)
    return wrapper