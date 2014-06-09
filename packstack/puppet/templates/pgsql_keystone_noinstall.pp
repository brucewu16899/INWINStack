
remote_database { 'keystone':
    ensure      => 'present',
    charset     => 'utf8',
    db_host     => '%(CONFIG_PGSQL_HOST)s',
    db_user     => '%(CONFIG_PGSQL_USER)s',
    db_password => '%(CONFIG_PGSQL_PW)s',
    provider    => 'postgresql',
}

remote_database_user { 'keystone_admin@%%':
    password_hash => pgsql_password('%(CONFIG_KEYSTONE_DB_PW)s' ),
    db_host       => '%(CONFIG_PGSQL_HOST)s',
    db_user       => '%(CONFIG_PGSQL_USER)s',
    db_password   => '%(CONFIG_PGSQL_PW)s',
    provider      => 'postgresql',
    require       => Remote_database['keystone'],
}

remote_database_grant { 'keystone_admin@%%/keystone':
    privileges  => "all",
    db_host     => '%(CONFIG_PGSQL_HOST)s',
    db_user     => '%(CONFIG_PGSQL_USER)s',
    db_password => '%(CONFIG_PGSQL_PW)s',
    provider    => 'postgresql',
    require     => Remote_database_user['keystone_admin@%%'],
}
