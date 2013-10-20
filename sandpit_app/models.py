from sqlalchemy import create_engine, Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship, sessionmaker

import config

Base = declarative_base()

class App(Base):
    __tablename__ = 'app'

    id = Column(String, primary_key=True)
    name = Column(String)
    app_type = Column(String)

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
    docker_id = Column(String)
    app_id = Column(String, ForeignKey('app.id'))

    app = relationship("App", backref=backref('images'))

    def __repr__(self):
        return "<AppImage(id='%s', app_id='%s', name='%s', docker_id='%s', status='%s')>" % (self.id, self.app_id, self.name, self.docker_id, self.status)


engine = create_engine('sqlite:///sandpit.sqlite', echo=True)

Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)
