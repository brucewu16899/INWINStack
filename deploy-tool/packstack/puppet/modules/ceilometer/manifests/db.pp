# Configures the ceilometer database
# This class will install the required libraries depending on the driver
# specified in the connection_string parameter
#
# == Parameters
#  [*database_connection*]
#    the connection string. format: [driver]://[user]:[password]@[host]/[database]
#
#  [*sync_db*]
#    enable dbsync.
#
#  [*mysql_module*]
#    (optional) Mysql puppet module version to use. Tested versions
#    are 0.9 and 2.2
#    Defaults to '0.9
#
class ceilometer::db (
  $database_connection = 'mysql://ceilometer:%(CONFIG_CEILOMETER_KS_PW)s@localhost/ceilometer',
  $sync_db             = true,
  $mysql_module        = '0.9',
) {

  include ceilometer::params

  Package<| title == 'ceilometer-common' |> -> Class['ceilometer::db']

  validate_re($database_connection,
    '(sqlite|mysql|postgresql|mongodb):\/\/(\S+:\S+@\S+\/\S+)?')

  case $database_connection {
    /^mysql:\/\//: {
      $backend_package = false

      if ($mysql_module >= 2.2) {
        include mysql::bindings::python
      } else {
        include mysql::python
      }
    }
    /^postgresql:\/\//: {
      $backend_package = $::ceilometer::params::psycopg_package_name
    }
    /^mongodb:\/\//: {
      $backend_package = $::ceilometer::params::pymongo_package_name
      #Bevis: if use mongodb, will remove sqlite setting at ceilometer.conf and /var/lib/ceilometer.sqlite db file
      ceilometer_config {
      'DEFAULT/sqlite_db': ensure => 'absent',
      }
      file {'remove-ceilometer-sqilte':
        path => '/var/lib/ceilometer/ceilometer.sqlite',
        ensure => 'absent',
      }
    }
    /^sqlite:\/\//: {
      $backend_package = $::ceilometer::params::sqlite_package_name
    }
    default: {
      fail('Unsupported backend configured')
    }
  }

  if $sync_db {
    $command = $::ceilometer::params::dbsync_command
  } else {
    $command = '/bin/true'
  }

  if $backend_package and !defined(Package[$backend_package]) {
    package {'ceilometer-backend-package':
      ensure => present,
      name   => $backend_package,
    }
  }

  ceilometer_config {
    'database/connection': value => $database_connection;
  }

  Ceilometer_config['database/connection'] ~> Exec['ceilometer-dbsync']

  exec { 'ceilometer-dbsync':
    command     => $command,
    path        => '/usr/bin',
    user        => $::ceilometer::params::user,
    refreshonly => true,
    logoutput   => on_failure,
    subscribe   => Ceilometer_config['database/connection']
  }

}
