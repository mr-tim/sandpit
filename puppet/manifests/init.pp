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


