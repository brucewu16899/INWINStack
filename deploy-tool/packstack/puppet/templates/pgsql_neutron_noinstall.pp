
remote_database { '%(CONFIG_NEUTRON_L2_DBNAME)s':
    ensure      => 'present',
    charset     => 'utf8',
    db_host     => '%(CONFIG_PGSQL_HOST)s',
    db_user     => '%(CONFIG_PGSQL_USER)s',
    db_password => '%(CONFIG_PGSQL_PW)s',
    provider    => 'postgresql',
}

remote_database_user { 'neutron@%%':
    password_hash => pgsql_password('%(CONFIG_NEUTRON_DB_PW)s' ),
    db_host       => '%(CONFIG_PGSQL_HOST)s',
    db_user       => '%(CONFIG_PGSQL_USER)s',
    db_password   => '%(CONFIG_PGSQL_PW)s',
    provider      => 'postgresql',
    require       => Remote_database['%(CONFIG_NEUTRON_L2_DBNAME)s'],
}

remote_database_grant { 'neutron@%%/%(CONFIG_NEUTRON_L2_DBNAME)s':
    privileges  => "all",
    db_host     => '%(CONFIG_PGSQL_HOST)s',
    db_user     => '%(CONFIG_PGSQL_USER)s',
    db_password => '%(CONFIG_PGSQL_PW)s',
    provider    => 'postgresql',
    require     => Remote_database_user['neutron@%%'],
}
