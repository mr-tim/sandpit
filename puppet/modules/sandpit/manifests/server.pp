define sandpit::server() {

  file { "/etc/nginx/sites-available/sandpit":
    source => "puppet:///modules/sandpit/nginx/sandpit.conf",
    ensure => "present"
  }

  file { "/etc/nginx/sites-enabled/sandpit":
    ensure => "link",
    target => "/etc/nginx/sites-available/sandpit",
    require => File["/etc/nginx/sites-available/sandpit"]
  }

  file { "/etc/init/sandpit-app.conf":
    source => "puppet:///modules/sandpit/sandpit-app.conf",
    ensure => "present"
  }

  file { "/etc/init/sandpit-celery.conf":
    source => "puppet:///modules/sandpit/sandpit-celery.conf",
    ensure => "present"
  }  

  service { "sandpit-app": 
    require => File["/etc/init/sandpit-app.conf"],
    ensure => "running"
  }

  service { "sandpit-celery": 
    require => File["/etc/init/sandpit-celery.conf"],
    ensure => "running"
  }

  file { ["/sandpit", "/sandpit/sessions", "/sandpit/sessions/data", "/sandpit/sessions/lock", "/sandpit/uploads"]:
    ensure => "directory",
    owner => "vagrant",
    group => "vagrant"
  }

  file { "/etc/nginx/nginx.conf":
    source => "puppet:///modules/sandpit/nginx/nginx.conf",
    ensure => "present",
    owner => 'root',
    group => 'root',
    notify => Service["nginx"]
  }

}
