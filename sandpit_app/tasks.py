from celery import Celery
from datetime import datetime

import docker
from models import Session, AppImage, AppInstance

celery = Celery('build_instance', broker='amqp://guest:guest@localhost:5672//')

@celery.task
def build_image(app_image_id):
    session = Session()
    app_image = session.query(AppImage).get(app_image_id)
    try:
        app_image.status = 'Building since %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        session.commit()

        kwargs = app_image.params

        f = app_image.app.app_type()
        container_id = f.build_image(**kwargs)

        docker_image_id = docker.commit(container_id, '_/AppImage/%s/%s' % (app_image.app.id, app_image.id))
        app_image.docker_image_id = docker_image_id
        app_image.status = 'Built'
        session.commit()
    except Exception as e:
        print "Exception whilst building image %s:" % app_image_id, e
        app_image.status = 'Build failed!'
        session.commit()


@celery.task
def run_image(app_image_id):
    db = Session()
    app_image = db.query(AppImage).get(app_image_id)
    f = app_image.app.app_type()
    container_id = f.run(app_image.app.id, app_image.docker_image_id)
    instance = AppInstance(app_image=app_image, container_id=container_id)
    db.add(instance)
    db.commit()
    

    





