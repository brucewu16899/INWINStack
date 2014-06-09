class {"neutron::db::postgresql":
    password      => "%(CONFIG_NEUTRON_DB_PW)s",
    dbname        => "%(CONFIG_NEUTRON_L2_DBNAME)s",
}
