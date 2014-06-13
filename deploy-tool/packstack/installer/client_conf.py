#!/usr/bin/env python
# -*- coding: utf-8 -*-

CLIENT_CONFIG = """
[general]
# Password for the PostgreSQL admin user
CONFIG_PGSQL_PW=password

# The password to use for the Keystone to access DB
CONFIG_KEYSTONE_DB_PW=password

# The token to use for the Keystone service api
CONFIG_KEYSTONE_ADMIN_TOKEN=admin

# The password to use for the Keystone admin user
CONFIG_KEYSTONE_ADMIN_PW=password

# The password to use for the Keystone demo user
CONFIG_KEYSTONE_DEMO_PW=password

# The password to use for the Glance to access DB
CONFIG_GLANCE_DB_PW=password

# The password to use for the Glance to authenticate with Keystone
CONFIG_GLANCE_KS_PW=password

# The password to use for the Cinder to access DB
CONFIG_CINDER_DB_PW=password

# The password to use for the Cinder to authenticate with Keystone
CONFIG_CINDER_KS_PW=password
# The password to use for the Nova to access DB
CONFIG_NOVA_DB_PW=password

# The password to use for the Nova to authenticate with Keystone
CONFIG_NOVA_KS_PW=password

# The password to use for Neutron to authenticate with Keystone
CONFIG_NEUTRON_KS_PW=password

# The password to use for Neutron to access DB
CONFIG_NEUTRON_DB_PW=password

#The CIDR network address for the external network
CONFIG_EXT_NET_IP_RANGE=172.20.0.0/16

#The gateway address for the external network
CONFIG_EXT_NET_GW_IP=172.20.0.1

#Start address for the external network
CONFIG_EXT_NET_IP_START=172.20.100.10

#End address for the external network
CONFIG_EXT_NET_IP_END=172.20.100.200

"""
