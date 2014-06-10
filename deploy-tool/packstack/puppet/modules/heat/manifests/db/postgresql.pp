#
# Class that configures postgresql for heat
#
# Requires the Puppetlabs postgresql module.
class heat::db::postgresql(
  $password,
  $dbname = 'heat',
  $user   = 'heat'
) {

  require postgresql::lib::python

  Postgresql::Server::Db[$dbname]    ~> Exec<| title == 'heat-manage db_sync' |>
  Package['python-psycopg2'] -> Exec<| title == 'heat-manage db_sync' |>

  postgresql::server::db { $dbname:
    user      =>  $user,
    password  =>  $password,
  }

}
