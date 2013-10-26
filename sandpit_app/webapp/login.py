import apiclient.discovery
from flask import Blueprint, redirect, render_template, request
import httplib2
from oauth2client.client import flow_from_clientsecrets

import config
from core import db
from models import User

login = Blueprint('login', __name__)

@login.route('/login')
def login_options():
    return render_template('login.html')

@login.route('/login/google')
def google_login_redirect():
    flow = get_flow()
    return redirect(flow.step1_get_authorize_url())

@login.route('/login/google/oauth2')
def google_login_landing():
    flow = get_flow()
    code = request.args.get('code')
    credentials = flow.step2_exchange(code)

    profile = get_api(credentials).userinfo().get().execute()

    email, name = profile['email'], profile['name']

    user = db.query(User).get(email)

    if user is None:
        user = User(email=email, name=name)
        db.add(user)
        db.commit()

    session = request.environ['beaker.session']
    session['username'] = user.email
    session.save()

    return redirect('/')

def get_flow():
    scope = 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile'
    redirect_uri = 'http://%s/login/google/oauth2' % request.host
    return flow_from_clientsecrets(config.client_secrets_location, scope=scope, redirect_uri=redirect_uri)

def get_api(credentials):
    http = httplib2.Http()
    http = credentials.authorize(http)
    return apiclient.discovery.build('oauth2', 'v2', http=http)

@login.route('/logout')
def logout():
    session = request.environ['beaker.session']
    session.delete()
    return render_template('logged_out.html')



