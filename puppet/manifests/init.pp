package { ["nginx", "curl", "htop", "nmap", "rabbitmq-server"]:
  ensure => "installed"
}

sandpit::server { 'sandpit-install':
  require => [Package['nginx'], Service['rabbitmq-server']]
}

service { "nginx":
  require => Package["nginx"],
  ensure => "running"
}

service { "rabbitmq-server":
  ensure => "running"
}

file { "/sandpit/sandpit.json":
  ensure => "present",
  source => "/vagrant/sandpit.json",
  require => File["/sandpit"],
  notify => Service["sandpit-app"]
}
