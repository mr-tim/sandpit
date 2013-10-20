Run celery with the following:

	celery -A tasks worker --loglevel=debug

Port forwarding under Mac OS: (www.dmuth.org/node/1404/web-development-port-80-and-443-vagrant)

	sudo ipfw add 100 fwd 127.0.0.1,8080 tcp from any to me 80
	sudo ipfw add 101 fwd 127.0.0.1,8443 tcp from any to me 443

Install dnsmasq, and add the following to /usr/local/etc/dnsmasq.conf

	address=/double-click.net/127.0.0.1
	address=/dev/127.0.0.1
