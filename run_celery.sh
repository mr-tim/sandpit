#!/bin/bash
source /vagrant/venv/bin/activate
cd /vagrant/sandpit_app
celery -A tasks worker --loglevel=debug