package { ["nginx", "curl", "htop", "nmap", "rabbitmq-server"]:
  ensure => "installed"
}

file { "/etc/nginx/sites-available/sandpit":
  source => "puppet:///modules/sandpit/nginx/sandpit.conf",
  ensure => "present"
}

file { "/etc/nginx/sites-enabled/sandpit":
  ensure => "link",
  target => "/etc/nginx/sites-available/sandpit",
  require => [File["/etc/nginx/sites-available/sandpit"], Package['nginx']]
}

file { "/etc/init/sandpit-app.conf":
  source => "puppet:///modules/sandpit/sandpit-app.conf",
  ensure => "present"
}

file { "/etc/init/sandpit-celery.conf":
  source => "puppet:///modules/sandpit/sandpit-celery.conf",
  ensure => "present"
}

service { "nginx":
  require => Package["nginx"],
  ensure => "running"
}

service { "sandpit-app": 
  require => File["/etc/init/sandpit-app.conf"],
  ensure => "running"
}

service { "rabbitmq-server":
  ensure => "running"
}

service { "sandpit-celery": 
  require => [File["/etc/init/sandpit-celery.conf"], Service['rabbitmq-server']],
  ensure => "running"
}

file { ["/sandpit", "/sandpit/sessions", "/sandpit/sessions/data", "/sandpit/sessions/lock"]:
  ensure => "directory",
  owner => "vagrant",
  group => "vagrant"
}


