#
# Class that configures postgresql for neutron
#
# Requires the Puppetlabs postgresql module.
class neutron::db::postgresql(
  $password,
  $dbname = 'neutron',
  $user   = 'neutron'
) {

    require postgresql::lib::python

    Postgresql::Server::Db[$dbname] ~> Exec<| title == 'neutron-db-manage upgrade' |>
    Package['python-psycopg2'] -> Exec<| title == 'neutron-db-manage upgrade' |>
    postgresql::server::db { $dbname:
        user      =>  $user,
        password  =>  $password,
    }

}