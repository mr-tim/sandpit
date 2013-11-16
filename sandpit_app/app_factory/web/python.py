from app_factory.web import WebAppBuilder
import docker

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
        image_id = docker.commit(container_id, self.docker_image_tag)
        return image_id

    @property
    def exposed_port(self):
        return 5000

    def run(self, app_id, docker_image_id):
        return docker.run(docker_image_id, ['/usr/local/bin/runapp'], ports=[self.exposed_port])

