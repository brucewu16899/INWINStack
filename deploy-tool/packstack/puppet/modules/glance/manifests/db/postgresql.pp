#
# Class that configures postgresql for glance
#
# Requires the Puppetlabs postgresql module.
class glance::db::postgresql(
  $password,
  $dbname = 'glance',
  $user   = 'glance'
) {

  require postgresql::lib::python
 
  Postgresql::Server::Db[$dbname] ~> Exec<| title == 'glance-manage db_sync' |>
  Package['python-psycopg2'] -> Exec<| title == 'glance-manage db_sync' |>

  postgresql::server::db { $dbname:
    user      =>  $user,
    password  =>  $password,
  }

}
