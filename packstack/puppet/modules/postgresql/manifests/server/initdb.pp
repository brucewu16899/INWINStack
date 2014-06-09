# PRIVATE CLASS: do not call directly
class postgresql::server::initdb {
  $ensure       = $postgresql::server::ensure
  $needs_initdb = $postgresql::server::needs_initdb
  $initdb_path  = $postgresql::server::initdb_path
  $datadir      = $postgresql::server::datadir
  $encoding     = $postgresql::server::encoding
  $locale       = $postgresql::server::locale
  $group        = $postgresql::server::group
  $user         = $postgresql::server::user

  if($ensure == 'present' or $ensure == true) {

    # cylee : create necessary folder for PostgreSQL
    if ($::osfamily == "Debian") {
        file { ["/var/lib/postgresql/", "/usr/lib/postgresql", "/etc/postgresql",
                "/var/lib/postgresql/${postgresql::server::version}",
                "/usr/lib/postgresql/${postgresql::server::version}",
                "/etc/postgresql/${postgresql::server::version}", 
                "/etc/postgresql/${postgresql::server::version}/main"] :
            ensure => directory,
            owner  => $user,
            group  => $group,
        } -> 
        exec { "change-owner" :
            command => "sudo chown ${user}:${group} -R /var/lib/postgresql/ /usr/lib/postgresql /etc/postgresql /var/run/postgresql",
            path    => "/usr/bin/:${postgresql::params::bindir}",
        }
    }

    # Make sure the data directory exists, and has the correct permissions.
    file { $datadir:
      ensure => directory,
      owner  => $user,
      group  => $group,
      #mode   => '0700',
    }

    if($needs_initdb == true) {
      # Build up the initdb command.
      #
      # We optionally add the locale switch if specified. Older versions of the
      # initdb command don't accept this switch. So if the user didn't pass the
      # parameter, lets not pass the switch at all.
      if ($::osfamily != "Debian") {
          $ic_base = "${initdb_path} --encoding '${encoding}' --pgdata '${datadir}'"
          $initdb_command = $locale ? {
            undef   => $ic_base,
            default => "${ic_base} --locale '${locale}'"
          }
      } else {
      # cylee : 05-20 : Create cluster first in 14.04, its workaround for now.

          $ic_base = "sudo /usr/bin/pg_createcluster -d '${datadir}'"
          $initdb_command = $locale ? {
            undef   => $ic_base,
            default => "${ic_base} --locale '${locale}' 9.3 main"
          }
      }

      # This runs the initdb command, we use the existance of the PG_VERSION
      # file to ensure we don't keep running this command.
      notice("PostgresSQL module trying to init DB")
      notice("=> ${initdb_command}")

      exec { 'postgresql_initdb':
        command   => $initdb_command,
        creates   => "${datadir}/PG_VERSION",
        #user      => $user,
        #group     => $group,
        logoutput => on_failure,
        before    => File[$datadir],
        path      => "/usr/bin/:${postgresql::params::bindir}",
        require   => Package['postgresql-server'],
      }
    }
  } else {
    # Purge data directory if ensure => absent
    file { $datadir:
      ensure  => absent,
      recurse => true,
      force   => true,
    }
  }
}
