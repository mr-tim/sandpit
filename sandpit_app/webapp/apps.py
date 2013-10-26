from datetime import datetime
from flask import Blueprint, redirect, render_template, request
import re

from core import current_user, db
from models import App, AppImage
import security
import tasks

def slugify(value):
    return re.sub('[^a-z0-9]', '-', value.strip().lower())


apps = Blueprint('apps', __name__)

@apps.route('/')
@security.logged_in
def list_apps():
    apps = current_user.apps
    return render_template('apps.html', current_tab='apps', apps=apps)

@apps.route('/app', methods=['POST'])
@security.logged_in
def create_app():
    app_id = slugify(request.form['newAppName'])
    app = App(id=app_id, name=request.form['newAppName'], app_type=request.form['appType'], owner=current_user)
    db.add(app)
    db.commit()
    return redirect('/')

@apps.route('/app/<app_id>')
@security.logged_in
def app_details(app_id):
    app = db.query(App).get(app_id)
    return render_template('app.html', app=app, current_tab='apps')

@apps.route('/app/<app_id>/createImage', methods=['GET'])
@security.logged_in
def create_image_form(app_id):
    app = db.query(App).get(app_id)

    if app.app_type == 'python':
        template = 'createPythonImage.html'
    else:
        template = 'unknownAppType.html'

    return render_template(template, app=app, current_tab='apps')

@apps.route('/app/<app_id>/createImage', methods=['POST'])
@security.logged_in
def create_image(app_id):
    app = db.query(App).get(app_id)

    if app.app_type == 'python':
        url = request.form['packageUrl']
        app_image = AppImage(name=request.form['name'], status='Pending build since %s' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'), app=app)
        db.add(app_image)
        db.commit()
        tasks.build_image.delay(app_image.id, 'shykes/pybuilder:latest', ['/usr/local/bin/buildapp', url])
    else:
        pass

    return redirect('/app/%s' % app.id)