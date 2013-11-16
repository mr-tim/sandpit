from flask import abort, redirect
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

def admin(f):
	@wraps(f)
	def wrapper(*args, **kwds):
		if current_user == None:
			return redirect('/login')
		elif current_user.is_admin:
			return f(*args, **kwds)
		else:
			abort(401)
	return wrapper