Sandpit
=======

Sandpit is a place for developers to have fun. It's a simple webapp that makes building [docker](http://www.docker.io/) containers and images simple, as well as setting them up an [nginx](http://wiki.nginx.org/Main) virtual host.

Getting Started
---------------
The easiest way to get started with sandpit is using Vagrant:

1. Clone the code
2. Visit https://cloud.google.com/console and set up a web application for OAuth2. Download the client_secrets.json file and put it in the root of the project. You'll need to decide on an address for your sandpit (eg, sandpit.example.com) - all your apps will be subdomains of this.
3. Run vagrant up - after a few seconds the app should start automatically.
4. Now you'll need to set up dns to get sandpit.example.com, and all the subdomains wired up (see "Making sandpit subdomains work" below).
5. You're done!

Making sandpit subdomains work
------------------------------
The main sandpit webapp is configured to listen to the main domain (eg, sandpit.example.com). When you create a new app (for example, my-first-app) it will automatically be set up with a virtual host that will have a subdomain based on the app id (eg, my-first-app.sandpit.example.com). To get this working for local you can use dnsmasq:

Install dnsmasq, and add the following to /usr/local/etc/dnsmasq.conf

    address=/sandpit.example.com/127.0.0.1
    
If you add dnsmasq (127.0.0.1) as a dns server, requests to *.sandpit.example.com should resolve to localhost.

By default, the vagrant box listens on 8080 - so you might want to forward port 80 to 8080:

Under Mac OS, this can be done as follows: (www.dmuth.org/node/1404/web-development-port-80-and-443-vagrant)

    sudo ipfw add 100 fwd 127.0.0.1,8080 tcp from any to me 80
    sudo ipfw add 101 fwd 127.0.0.1,8443 tcp from any to me 443
