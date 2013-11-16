import docker
import nginx

class WebAppBuilder(object):
    def app_type(self):
        return 'web'

    @property
    def exposed_port(self):
        return 8080

    def run(self, app_id, docker_image_id):
        return docker.run(docker_image_id, ports=[self.exposed_port])

    def create_front_end(self, container_id, vhost):
        process_details = docker.inspect(container_id)
        forwarded_port = process_details["NetworkSettings"]["PortMapping"]["Tcp"][str(self.exposed_port)]
        backend = "http://localhost:%s" % forwarded_port
        nginx.configure_vhost(vhost, backend)