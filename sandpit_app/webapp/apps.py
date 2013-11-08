from datetime import datetime
from flask import Blueprint, redirect, render_template, request
import json
import re
from wtforms import Form, StringField, validators

import app_factory
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
        params = extract_build_params(app, form)
        app_image.params = json.dumps(params)
        db.add(app_image)
        db.commit()

        tasks.build_image.delay(app_image.id)

        return redirect('/app/%s' % app.id)
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

        field = StringField(field_desc['name'], description=desc)
        setattr(ImageForm, field_name, field)

    form = ImageForm(form_values)

    return form


def extract_build_params(app, form):
    params = {}
    param_names = set([n for n, d in app.app_type.build_image_params])
    for f in form:
        if f.name in param_names:
            params[f.name] = f.data

    return params


