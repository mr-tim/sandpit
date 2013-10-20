from celery import Celery
from datetime import datetime

import config
import docker
from models import Session, AppImage
import nginx

celery = Celery('build_instance', broker='sqla+sqlite:///celerydb.sqlite')

@celery.task
def build_image(app_image_id, base_image, args):
    print "Building image: %s, %r" % (base_image, args)
    session = Session()
    app_image = session.query(AppImage).get(app_image_id)
    app_image.status = 'Building since %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    session.commit()

    container_id = docker.run(base_image, args)
    docker.wait(container_id)
    docker_image_id = docker.commit(container_id, '_/AppImage/%s/%s' % (app_image.app.id, app_image.id))
    app_image.docker_id = docker_image_id
    app_image.status = 'Built'
    session.commit()


@celery.task
def run_image(app_image_id):
    session = Session()
    app_image = session.query(AppImage).get(app_image_id)
    docker_image_id = app_image.docker_id
    process = docker.run(docker_image_id, ['/usr/local/bin/runapp'], ports=[5000])
    process_details = docker.inspect(process)[0]

    forwarded_port = process_details["NetworkSettings"]["PortMapping"]["Tcp"]["5000"]

    vhost = "%s.%s" % (app_image.app.id, config.domain_suffix)
    backend = "http://localhost:%s" % forwarded_port

    nginx.configure_vhost(vhost, backend)

    





