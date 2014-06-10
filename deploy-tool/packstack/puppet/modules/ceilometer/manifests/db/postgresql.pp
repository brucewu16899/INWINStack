#
# Class that configures postgresql for ceilometer
#
# Requires the Puppetlabs postgresql module.
class ceilometer::db::postgresql(
  $password,
  $dbname = 'ceilometer',
  $user   = 'ceilometer'
) {

  require postgresql::lib::python

  Postgresql::Server::Db[$dbname]    ~> Exec<| title == 'ceilometer-dbsync' |>
  Package['python-psycopg2'] -> Exec<| title == 'ceilometer-dbsync' |>

  postgresql::server::db { $dbname:
    user      =>  $user,
    password  =>  $password,
  }

}