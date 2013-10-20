from datetime import datetime
from flask import Blueprint, redirect, render_template, request
import re

from models import App, AppImage, Session
import tasks

def slugify(value):
    return re.sub('[^a-z0-9]', '-', value.strip().lower())


apps = Blueprint('apps', __name__)

@apps.route('/')
def apps():
    session = Session()
    apps = session.query(App).order_by('name').all()
    return render_template('apps.html', current_tab='apps', apps=apps)

@apps.route('/app', methods=['POST'])
def create_app():
    app_id = slugify(request.form['newAppName'])
    app = App(id=app_id, name=request.form['newAppName'], app_type=request.form['appType'])
    session = Session()
    session.add(app)
    session.commit()
    return redirect('/')

@apps.route('/app/<app_id>')
def app_details(app_id):
    session = Session()
    app = session.query(App).get(app_id)
    return render_template('app.html', app=app, current_tab='apps')

@apps.route('/app/<app_id>/createImage', methods=['GET'])
def create_image_form(app_id):
    session = Session()
    app = session.query(App).get(app_id)

    if app.app_type == 'python':
        template = 'createPythonImage.html'
    else:
        template = 'unknownAppType.html'

    return render_template(template, app=app, current_tab='apps')

@apps.route('/app/<app_id>/createImage', methods=['POST'])
def create_image(app_id):
    session = Session()
    app = session.query(App).get(app_id)

    if app.app_type == 'python':
        url = request.form['packageUrl']
        app_image = AppImage(name=request.form['name'], status='Pending build since %s' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'), app=app)
        session.add(app_image)
        session.commit()
        tasks.build_image.delay(app_image.id, 'shykes/pybuilder:latest', ['/usr/local/bin/buildapp', url])
    else:
        pass

    return redirect('/app/%s' % app.id)