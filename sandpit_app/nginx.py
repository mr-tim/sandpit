import subprocess
import tempfile

def configure_vhost(vhost, backend):
    nginx_config = """server {
  server_name %s;
  
  location / {
    proxy_pass %s;
  }
}""" % (vhost, backend)

    nginx_config_filename = "/etc/nginx/sites-enabled/%s" % vhost
    
    fh, tmp_file = tempfile.mkstemp()

    with open(tmp_file, 'w+') as nginx_config_file:
        nginx_config_file.write(nginx_config)

    p = subprocess.Popen(['sudo', 'mv', tmp_file, nginx_config_filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()

    reload_config()

def reload_config():
    p = subprocess.Popen(['sudo', 'nginx', '-s', 'reload'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()