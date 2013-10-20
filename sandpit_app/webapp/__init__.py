from flask import Flask

from admin import admin
from apps import apps

app = Flask(__name__)
app.register_blueprint(admin)
app.register_blueprint(apps)
