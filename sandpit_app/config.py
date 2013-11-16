import json
import os
from os.path import join

sandpit_dir = os.getenv('SANDPIT_DIR', '/sandpit')
uploads_dir = join(sandpit_dir, 'uploads')
client_secrets_location = '/vagrant/client_secrets.json'

with open(join(sandpit_dir, 'sandpit.json')) as config_file:
	values = json.load(config_file)
	l = locals()
	for k, v in values.iteritems():
		l[k] = v