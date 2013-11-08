from app_factory.web import WebAppBuilder
import config
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
        process = docker.run(docker_image_id, ['/usr/local/bin/runapp'], ports=[5000])
        process_details = docker.inspect(process)[0]

        forwarded_port = process_details["NetworkSettings"]["PortMapping"]["Tcp"]["5000"]

        vhost = "%s.%s" % (app_id, config.domain_suffix)
        backend = "http://localhost:%s" % forwarded_port

        nginx.configure_vhost(vhost, backend)
