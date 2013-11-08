from celery import Celery
from datetime import datetime
import json

import docker
from models import Session, AppImage

celery = Celery('build_instance', broker='amqp://guest:guest@localhost:5672//')

@celery.task
def build_image(app_image_id):
    session = Session()
    app_image = session.query(AppImage).get(app_image_id)
    try:
        app_image.status = 'Building since %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        session.commit()

        kwargs = json.loads(app_image.params)

        f = app_image.app.app_type()
        container_id = f.build_image(**kwargs)

        docker_image_id = docker.commit(container_id, '_/AppImage/%s/%s' % (app_image.app.id, app_image.id))
        app_image.docker_id = docker_image_id
        app_image.status = 'Built'
        session.commit()

        run_image.delay(app_image_id)
    except Exception:
        app_image.status = 'Build failed!'
        session.commit()


@celery.task
def run_image(app_image_id):
    session = Session()
    app_image = session.query(AppImage).get(app_image_id)
    f = app_image.app.app_type()
    f.run(app_image.app.id, app_image.docker_id)
    

    





