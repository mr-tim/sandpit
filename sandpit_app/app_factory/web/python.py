from app_factory.web import WebAppBuilder
import docker
import nginx

class Shykes(WebAppBuilder):
    name = "Python webapp - Shykes"
    build_image_params = [ 
        ('package_url', { 'name': 'Package Url', 'placeholder': 'http://path/to/package.tar.gz' })
    ]

    def build_image(self, package_url):
        print "Building shykes python app image"
        base_image, args = 'shykes/pybuilder:latest', ['/usr/local/bin/buildapp', package_url]
        print "Building image: %s, %r" % (base_image, args)
        container_id = docker.run(base_image, args)
        docker.wait(container_id)
        return container_id

    def run(self, app_id, docker_image_id):
        return docker.run(docker_image_id, ['/usr/local/bin/runapp'], ports=[5000])

    def create_front_end(self, container_id, vhost):
        process_details = docker.inspect(container_id)
        forwarded_port = process_details["NetworkSettings"]["PortMapping"]["Tcp"]["5000"]
        backend = "http://localhost:%s" % forwarded_port
        nginx.configure_vhost(vhost, backend)
