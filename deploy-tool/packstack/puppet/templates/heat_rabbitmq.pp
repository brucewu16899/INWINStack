class { 'heat':
    keystone_host     => '%(CONFIG_KEYSTONE_HOST)s',
    keystone_password => '%(CONFIG_HEAT_KS_PW)s',
    auth_uri          => 'http://%(CONFIG_KEYSTONE_HOST)s:35357/v2.0',
    rpc_backend       => 'heat.openstack.common.rpc.impl_kombu',
    rabbit_host       => '%(CONFIG_AMQP_HOST)s',
    rabbit_userid     => '%(CONFIG_AMQP_AUTH_USER)s',
    rabbit_password   => '%(CONFIG_AMQP_AUTH_PASSWORD)s',
    verbose           => true,
    debug             => %(CONFIG_DEBUG_MODE)s,
    sql_connection    => "postgresql://heat:%(CONFIG_HEAT_DB_PW)s@%(CONFIG_PGSQL_HOST)s/heat",
}
