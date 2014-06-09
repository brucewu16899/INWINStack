# PRIVATE CLASS: do not call directly
class postgresql::server::install {
  $package_ensure      = $postgresql::server::package_ensure
  $package_name        = $postgresql::server::package_name
  $client_package_name = $postgresql::server::client_package_name

  # This is necessary to ensure that the extra client package that was
  # installed automatically by the server package is removed and all
  # of its dependencies are removed also. Without this later installation
  # of the native Ubuntu packages will fail.
  if($::operatingsystem == 'Ubuntu' and $package_ensure == 'absent') {
    # This is an exec, because we want to invoke autoremove.
    #
    # An alternative would be to have a full list of packages, but that seemed
    # more problematic to maintain, not to mention the conflict with the
    # client class will create duplicate resources.
    exec { 'apt-get-autoremove-postgresql-client-XX':
      command   => "apt-get autoremove --purge --yes ${client_package_name}",
      onlyif    => "dpkg -l ${client_package_name} | grep -e '^ii'",
      logoutput => on_failure,
      path      => '/usr/bin:/bin:/usr/sbin/:/sbin',
    }

    # This will clean up anything we miss
    exec { 'apt-get-autoremove-postgresql-client-brute':
      command   => "apt-get remove postgresql postgresql-common",
      onlyif    => "dpkg-query -l postgresql | grep -e '^ii'",
      logoutput => on_failure,
      path      => '/usr/bin:/bin:/usr/sbin/:/sbin',
    }
  }

  $_package_ensure = $package_ensure ? {
    true     => 'present',
    false    => 'purged',
    'absent' => 'purged',
    default => $package_ensure,
  }

  # Bevis : delete postgresql-common packake in here

  package { 'postgresql-server':
    ensure => $_package_ensure,
    name   => $package_name,
    # cyle : create user and cluster managment tool in common package.
    # Bevis : 2014.5.19
    #require => Package['postgresql-common'],
    # This is searched for to create relationships with the package repos, be
    # careful about its removal
    tag    => 'postgresql',
  }
  
 }
