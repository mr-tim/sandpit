import os.path
import shutil
import tempfile

from app_factory.web import WebAppBuilder
import docker

DOCKERFILE = """FROM ubuntu:12.04
RUN echo "deb http://gb.archive.ubuntu.com/ubuntu precise main restricted" > /etc/apt/sources.list
RUN echo "deb http://gb.archive.ubuntu.com/ubuntu precise-updates main restricted" >> /etc/apt/sources.list
RUN echo "deb http://gb.archive.ubuntu.com/ubuntu precise universe" >> /etc/apt/sources.list
RUN echo "deb http://gb.archive.ubuntu.com/ubuntu precise-updates universe" >> /etc/apt/sources.list
RUN echo "deb http://gb.archive.ubuntu.com/ubuntu precise multiverse" >> /etc/apt/sources.list
RUN echo "deb http://gb.archive.ubuntu.com/ubuntu precise-updates multiverse" >> /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y openjdk-7-jre-headless tomcat7
RUN rm -rf /var/lib/tomcat7/webapps/*
ADD webapps /var/lib/tomcat7/webapps/
EXPOSE 8080
ENTRYPOINT service tomcat7 start && tail -f /var/lib/tomcat7/logs/catalina.out"""

class UploadedWar(WebAppBuilder):
    name = "Java webapp - Uploaded war"
    build_image_params = [
        ('context_path', { 'name': 'Context path' }),
        ('war', { 'name': 'Upload war', 'field_type': 'file' })
    ]

    def build_image(self, war, context_path):
        build_dir = tempfile.mkdtemp()
        with open(os.path.join(build_dir, 'Dockerfile'), 'w+') as dockerfile:
            dockerfile.write(DOCKERFILE)
        os.makedirs(os.path.join(build_dir, 'webapps'))
        if context_path.startswith('/'):
            context_path = context_path[1:]
        if len(context_path) == 0:
            context_path = 'ROOT'
        shutil.copyfile(war, os.path.join(build_dir, 'webapps', context_path+'.war'))
        image_id = docker.build(build_dir, self.docker_image_tag)
        shutil.rmtree(build_dir)
        return image_id
