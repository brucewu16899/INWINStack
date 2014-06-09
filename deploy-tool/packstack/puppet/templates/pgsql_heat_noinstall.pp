
remote_database { 'heat':
    ensure      => 'present',
    charset     => 'utf8',
    db_host     => '%(CONFIG_PGSQL_HOST)s',
    db_user     => '%(CONFIG_PGSQL_USER)s',
    db_password => '%(CONFIG_PGSQL_PW)s',
    provider    => 'postgresql',
}

remote_database_user { 'heat@%%':
    password_hash => pgsql_password('%(CONFIG_HEAT_DB_PW)s'),
    db_host       => '%(CONFIG_PGSQL_HOST)s',
    db_user       => '%(CONFIG_PGSQL_USER)s',
    db_password   => '%(CONFIG_PGSQL_PW)s',
    provider      => 'postgresql',
    require       => Remote_database['heat'],
}

remote_database_grant { 'heat@%%/heat':
    privileges  => "all",
    db_host     => '%(CONFIG_PGSQL_HOST)s',
    db_user     => '%(CONFIG_PGSQL_USER)s',
    db_password => '%(CONFIG_PGSQL_PW)s',
    provider    => 'postgresql',
    require     => Remote_database_user['heat@%%'],
}
