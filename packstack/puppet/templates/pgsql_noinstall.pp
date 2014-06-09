
package { 'postgresql':
    ensure => 'present',
}

Package ['pgsql'] -> Remote_database<||>
Package ['pgsql'] -> Remote_database_user<||>
Package ['pgsql'] -> Remote_database_grant<||>
