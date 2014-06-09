class {"heat::db::postgresql":
    password      => "%(CONFIG_HEAT_DB_PW)s",
    allowed_hosts => "%%",
    charset       => "utf8",
}
