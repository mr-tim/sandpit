from flask import Blueprint, render_template
import json

import docker

admin = Blueprint('admin', __name__)

@admin.route('/admin')
def admin_home():
    images = sorted(docker.images(), key=lambda i: i['repository'])
    processes = sorted(docker.ps(), key=lambda p: p['image'])
    return render_template('admin.html', images=images, processes=processes, current_tab='admin')

@admin.route('/admin/image/<image_id>')
def image(image_id):
    image = json.dumps(docker.inspect(image_id), indent=2)
    return render_template('image.html', image=image, current_tab='admin')

@admin.route('/admin/process/<process_id>')
def process(process_id):
    process = json.dumps(docker.inspect(process_id), indent=2)
    return render_template('process.html', process=process, current_tab='admin')