from flask import g, request
from werkzeug.local import LocalProxy

from models import User, Session

def get_or_create_db_session():
    if not hasattr(g, 'db'):
        g.db = Session()
    return g.db

db = LocalProxy(get_or_create_db_session)

def load_user_from_session():
    user = None
    session = request.environ['beaker.session']
    if 'username' in session:
        username = session['username']
        if should_load_user(username):
            user = load_user(session['username'])
            if user is not None:
                g.user = user
        else:
            user = g.get('user', None)
    return user

def should_load_user(username):
    return (not hasattr(g, 'user')) or (g.user.email != username)

def load_user(username):
    return db.query(User).get(username)

current_user = LocalProxy(load_user_from_session)