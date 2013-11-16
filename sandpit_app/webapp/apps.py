from datetime import datetime
from flask import Blueprint, redirect, render_template, request
import json
import os
import os.path
import re
from werkzeug import secure_filename
from wtforms import Form, FileField, StringField, validators

import app_factory
import config
from core import current_user, db
import docker
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
    app_types = app_factory.index.app_types()
    return render_template('apps.html', current_tab='apps', apps=apps, app_types=app_types)

@apps.route('/app', methods=['POST'])
@security.logged_in
def create_app():
    app_id = slugify(request.form['newAppName'])
    app = App(id=app_id, name=request.form['newAppName'], app_type_id=request.form['appType'], owner=current_user)
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
def display_new_image_form(app_id):
    app = db.query(App).get(app_id)
    form = create_new_image_form(app)
    return render_template('createImage.html', app=app, current_tab='apps', form=form)

@apps.route('/app/<app_id>/createImage', methods=['POST'])
@security.logged_in
def create_image(app_id):
    app = db.query(App).get(app_id)
    form = create_new_image_form(app, request.form)

    if form.validate():
        app_image = AppImage(name=form.image_name.data, status='Pending build since %s' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'), app=app)
        db.add(app_image)
        db.flush()
        params = extract_build_params(app, app_image, form)
        app_image.params_json = json.dumps(params)
        db.commit()

        tasks.build_image.delay(app_image.id)

        return redirect_to_app_page(app)
    else:
        return render_template('createImage.html', app=app, current_tab='apps', form=form)

def create_new_image_form(app, form_values=None):
    class ImageForm(Form):
        image_name = StringField('Image Name', [validators.InputRequired()])

    for field_name, field_desc in app.app_type.build_image_params:
        print "%s => %r" % (field_name, field_desc)
        desc  = {}
        if 'placeholder' in field_desc:
            desc['placeholder'] = field_desc['placeholder']
        T = StringField
        if 'field_type' in field_desc:
            if field_desc['field_type'] == 'file':
                T = FileField

        field = T(field_desc['name'], description=desc)
        setattr(ImageForm, field_name, field)

    form = ImageForm(form_values)

    return form

def extract_build_params(app, app_image, form):
    params = {}
    param_names = set([n for n, d in app.app_type.build_image_params])
    for f in form:
        if f.name in param_names:
            params[f.name] = f.data
            if isinstance(f, FileField):
                upload_file_path = os.path.join(config.uploads_dir, app.id, str(app_image.id), f.name)
                if not os.path.exists(upload_file_path):
                    os.makedirs(upload_file_path)
                uploaded_file = request.files[f.name]
                upload_filename = os.path.join(upload_file_path, secure_filename(uploaded_file.filename))
                uploaded_file.save(upload_filename)
                params[f.name] = upload_filename

    return params

@apps.route('/app/<app_id>/createInstance', methods=['POST'])
def create_instance(app_id):
    app = db.query(App).get(app_id)
    image = app.image(int(request.form.get('image_id', -1)))

    if image:
        tasks.run_image(image.id)

    return redirect_to_app_page(app)

@apps.route('/app/<app_id>/instance/<int:instance_id>/delete', methods=['POST'])
def delete_instance(app_id, instance_id):
    app = db.query(App).get(app_id)
    instance = app.instance(instance_id)

    if instance and instance.status != 'Running' and not instance.is_live:
        docker.rm(instance.container_id)
        db.delete(instance)
        db.commit()

    return redirect_to_app_page(app)

@apps.route('/app/<app_id>/instance/<int:instance_id>/stop', methods=['POST'])
def stop_instance(app_id, instance_id):
    app = db.query(App).get(app_id)
    instance = app.instance(instance_id)

    if instance and instance.status == 'Running' and not instance.is_live:
        docker.stop(instance.container_id)

    return redirect_to_app_page(app)

@apps.route('/app/<app_id>/instance/<int:instance_id>/start', methods=['POST'])
def start_instance(app_id, instance_id):
    app = db.query(App).get(app_id)
    instance = app.instance(instance_id)

    if instance and instance.status != 'Running':
        docker.start(instance.container_id)

    return redirect_to_app_page(app)

@apps.route('/app/<app_id>/instance/<int:instance_id>/goLive', methods=['POST'])
def go_live(app_id, instance_id):
    app = db.query(App).get(app_id)
    instance = app.instance(instance_id)

    if instance and instance.status == 'Running':
        for i in app.instances:
            i.is_live = False
        instance.is_live = True

        f = app.app_type()
        f.create_front_end(instance.container_id, app.url[7:])

        db.commit()        

    return redirect_to_app_page(app)


def redirect_to_app_page(app):
    return redirect('/app/%s' % app.id)
