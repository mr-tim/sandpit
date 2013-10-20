from datetime import datetime
from flask import Flask, redirect, render_template, request
import json
import re

import docker
from models import App, AppImage, Session
import tasks

app = Flask(__name__)


def slugify(value):
    return re.sub('[^a-z0-9]', '-', value.strip().lower())


@app.route('/')
def apps():
    session = Session()
    apps = session.query(App).order_by('name').all()
    return render_template('apps.html', current_tab='apps', apps=apps)

@app.route('/admin')
def admin():
    images = sorted(docker.images(), key=lambda i: i['repository'])
    processes = sorted(docker.ps(), key=lambda p: p['image'])
    return render_template('admin.html', images=images, processes=processes, current_tab='admin')

@app.route('/admin/image/<image_id>')
def image(image_id):
    image = json.dumps(docker.inspect(image_id), indent=2)
    return render_template('image.html', image=image, current_tab='admin')

@app.route('/admin/process/<process_id>')
def process(process_id):
    process = json.dumps(docker.inspect(process_id), indent=2)
    return render_template('process.html', process=process, current_tab='admin')

@app.route('/app', methods=['POST'])
def create_app():
    app_id = slugify(request.form['newAppName'])
    app = App(id=app_id, name=request.form['newAppName'], app_type=request.form['appType'])
    session = Session()
    session.add(app)
    session.commit()
    return redirect('/')

@app.route('/app/<app_id>')
def app_details(app_id):
    session = Session()
    app = session.query(App).get(app_id)
    return render_template('app.html', app=app, current_tab='apps')

@app.route('/app/<app_id>/createImage', methods=['GET'])
def create_image_form(app_id):
    session = Session()
    app = session.query(App).get(app_id)

    if app.app_type == 'python':
        template = 'createPythonImage.html'
    else:
        template = 'unknownAppType.html'

    return render_template(template, app=app, current_tab='apps')

@app.route('/app/<app_id>/createImage', methods=['POST'])
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)