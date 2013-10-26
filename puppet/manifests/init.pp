package { ["nginx", "curl", "htop", "nmap"]:
  ensure => "installed"
}

file { "/etc/nginx/sites-available/sandpit":
  source => "puppet:///modules/sandpit/sandpit.conf",
  ensure => "present"
}

file { "/etc/nginx/sites-enabled/sandpit":
  ensure => "link",
  target => "/etc/nginx/sites-available/sandpit",
  require => [File["/etc/nginx/sites-available/sandpit"], Package['nginx']]
}

file { "/etc/init/sandpit_app.conf":
  source => "puppet:///modules/sandpit/sandpit_app.conf",
  ensure => "present"
}

file { "/etc/init/sandpit_celery.conf":
  source => "puppet:///modules/sandpit/sandpit_celery.conf",
  ensure => "present"
}

service { "nginx":
  require => Package["nginx"],
  ensure => "running"
}

service { "sandpit_app": 
  require => File["/etc/init/sandpit_app.conf"],
  ensure => "running"
}

service { "sandpit_celery": 
  require => File["/etc/init/sandpit_celery.conf"],
  ensure => "running"
}

file { ["/sandpit", "/sandpit/sessions", "/sandpit/sessions/data", "/sandpit/sessions/lock"]:
  ensure => "directory",
  owner => "vagrant",
  group => "vagrant"
}


