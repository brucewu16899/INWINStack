class {"keystone::db::postgresql":
    user          => 'keystone_admin',
    password      => "%(CONFIG_KEYSTONE_DB_PW)s",
}
