class { 'postgresql::server':
  ip_mask_deny_postgres_user => '0.0.0.0/32',
  ip_mask_allow_all_users    => '0.0.0.0/0',
  listen_addresses           => '*',
  #ipv4acl                    => 'host all all 172.0.0.0/8 password',
  user                       => "%(CONFIG_PGSQL_USER)s",
  postgres_password          => "%(CONFIG_PGSQL_PW)s",
  needs_initdb               => true,
  locale                     => 'en_US.UTF-8',
}
