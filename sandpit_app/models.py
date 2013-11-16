import json
from sqlalchemy import create_engine, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship, sessionmaker

import app_factory
import config
import docker

Base = declarative_base()

def json_field(locator):
    def getter(self):
        v = locator(self)
        return {} if v is None else json.loads(v)
    return getter


class App(Base):
    __tablename__ = 'app'

    id = Column(String, primary_key=True)
    name = Column(String)
    app_type_id = Column(String)
    owner_email = Column(String, ForeignKey('user.email'))

    owner = relationship('User', backref=backref('apps'))

    def image(self, app_image_id):
        i = filter(lambda img: img.id == app_image_id, self.images)
        return i[0] if len(i) else None

    @property
    def instances(self):
        instances = []
        for app_image in self.images:
            instances.extend(app_image.instances)
        return instances

    def instance(self, app_instance_id):
        i = filter(lambda inst: inst.id == app_instance_id, self.instances)
        return i[0] if len(i) else None

    @property
    def app_type(self):
        return app_factory.index.get(self.app_type_id)

    @property
    def url(self):
        return "http://%s.%s" % (self.id, config.domain_suffix)

    def __repr__(self):
        return "<App(id='%s', name='%s')>" % (self.id, self.name)


class AppImage(Base):
    __tablename__ = 'app_image'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    status = Column(String)
    docker_image_id = Column(String)
    params_json = Column(String)
    app_id = Column(String, ForeignKey('app.id'))

    app = relationship("App", backref=backref('images'))

    params = property(json_field(lambda self: self.params_json))

    def __repr__(self):
        return "<AppImage(id='%s', app_id='%s', name='%s', docker_id='%s', status='%s')>" % (self.id, self.app_id, self.name, self.docker_image_id, self.status)


class AppInstance(Base):
    __tablename__ = 'app_instance'

    id = Column(Integer, primary_key=True)
    container_id = Column(String)
    app_image_id = Column(String, ForeignKey('app_image.id'))
    is_live = Column(Boolean)

    app_image = relationship("AppImage", backref=backref('instances'))

    @property
    def status(self):
        container_info = docker.inspect(self.container_id)
        if container_info:
            if container_info['State']['Running'] == True:
                return "Running"
            else:
                return "Stopped"

        return "Unknown"

    def __repr__(self):
        return "<AppInstance(id='%s', container_id='%s', app_image_id='%s')>" % (self.id, self.container_id, self.app_image_id)


class User(Base):
    __tablename__ = 'user'

    email = Column(String, primary_key=True)
    name = Column(String)
    is_admin = Column(Boolean, default=False)



engine = create_engine('sqlite:///sandpit.sqlite', echo=True)

Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)
