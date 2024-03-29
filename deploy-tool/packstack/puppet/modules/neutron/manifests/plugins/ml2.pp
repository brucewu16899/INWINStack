#
# Copyright (C) 2013 eNovance SAS <licensing@enovance.com>
#
# Author: Emilien Macchi <emilien.macchi@enovance.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# Configure the neutron server to use the ML2 plugin.
# This configures the plugin for the API server, but does nothing
# about configuring the agents that must also run and share a config
# file with the OVS plugin if both are on the same machine.
#
# === Parameters
#
# [*type_drivers*]
#   (optional) List of network type driver entrypoints to be loaded
#   from the neutron.ml2.type_drivers namespace.
#   Could be an array that can have these elements:
#   local, flat, vlan, gre, vxlan
#   Defaults to ['local', 'flat', 'vlan', 'gre', 'vxlan'].
#
# [*tenant_network_types*]
#   (optional) Ordered list of network_types to allocate as tenant networks.
#   The value 'local' is only useful for single-box testing
#   but provides no connectivity between hosts.
#   Should be an array that can have these elements:
#   local, flat, vlan, gre, vxlan
#   Defaults to ['local', 'flat', 'vlan', 'gre', 'vxlan'].
#
# [*mechanism_drivers*]
#   (optional) An ordered list of networking mechanism driver
#   entrypoints to be loaded from the neutron.ml2.mechanism_drivers namespace.
#   Should be an array that can have these elements:
#   logger, test, linuxbridge, openvswitch, hyperv, ncs, arista, cisco_nexus,
#   l2population.
#   Default to ['openvswitch', 'linuxbridge'].
#
# [*flat_networks*]
#   (optional) List of physical_network names with which flat networks
#   can be created. Use * to allow flat networks with arbitrary
#   physical_network names.
#   Should be an array.
#   Default to *.
#
# [*network_vlan_ranges*]
#   (optional) List of <physical_network>:<vlan_min>:<vlan_max> or
#   <physical_network> specifying physical_network names
#   usable for VLAN provider and tenant networks, as
#   well as ranges of VLAN tags on each available for
#   allocation to tenant networks.
#   Should be an array with vlan_min = 1 & vlan_max = 4094 (IEEE 802.1Q)
#   Default to empty.
#
# [*tunnel_id_ranges*]
#   (optional) Comma-separated list of <tun_min>:<tun_max> tuples
#   enumerating ranges of GRE tunnel IDs that are
#   available for tenant network allocation
#   Should be an array with tun_max +1 - tun_min > 1000000
#   Default to empty.
#
# [*vxlan_group*]
#   (optional) Multicast group for VXLAN.
#   Multicast group for VXLAN. If unset, disables VXLAN enable sending allocate
#   broadcast traffic to this multicast group. When left unconfigured, will
#   disable multicast VXLAN mode
#   Should be an Multicast IP (v4 or v6) address.
#   Default to 'None'.
#
# [*vni_ranges*]
#   (optional) Comma-separated list of <vni_min>:<vni_max> tuples
#   enumerating ranges of VXLAN VNI IDs that are
#   available for tenant network allocation.
#   Min value is 0 and Max value is 16777215.
#   Default to empty.
#
# [*enable_security_group*]
#   (optionnal) Enable the security group API or not.
#   Since the ML2 plugin can concurrently support different L2 agents (or other
#   mechanisms) with different configurations, we need to set something to the
#   firewall_driver flag to enable security group API.
#   Defaults to false.
#
# [*firewall_driver*]
#   (optionnal) Set a firewall driver value.
#   If enable_security_group is enabled, it should be either true or a custom
#   firewall driver.
#   Defaults to true.

class neutron::plugins::ml2 (
  $type_drivers          = ['local', 'flat', 'vlan', 'gre', 'vxlan'],
  $tenant_network_types  = ['local', 'flat', 'vlan', 'gre', 'vxlan'],
  $mechanism_drivers     = ['openvswitch', 'linuxbridge'],
  $flat_networks         = ['*'],
  $network_vlan_ranges   = ['physnet1:1000:2999'],
  $tunnel_id_ranges      = ['20:100'],
  $vxlan_group           = '224.0.0.1',
  $vni_ranges            = ['10:100'],
  $enable_security_group = false,
  $enable_tunneling      = true,
  $firewall_driver       = 'neutron.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver',
  $local_ip              = false,
  $tunnel_types          = ['gre'],
  $integration_bridge    = 'br-int',
  $tunnel_bridge         = 'br-tun',
  $vxlan_udp_port        = 4789,
  $polling_interval      = 2,

) {

  include neutron::params

  # test mechanism drivers
  validate_array($mechanism_drivers)
  if ! $mechanism_drivers {
    warning('Without networking mechanism driver, ml2 will not communicate with L2 agents')
  }

  # Some platforms do not have a dedicated ml2 plugin package
  # In RH, the link is used to start Neutron process but in Debian, it's used only
  # to manage database synchronization.
  if $::neutron::params::ml2_server_package {
    package { 'neutron-plugin-ml2':
      ensure => present,
      name   => $::neutron::params::ml2_server_package,
    }
    Package['neutron-plugin-ml2'] -> Neutron_plugin_ml2<||>
    file {'/etc/neutron/plugin.ini':
      ensure  => link,
      target  => '/etc/neutron/plugins/ml2/ml2_conf.ini',
      require => Package['neutron-plugin-ml2']
    }
  } else {
      file {'/etc/neutron/plugin.ini':
        ensure  => link,
        target  => '/etc/neutron/plugins/ml2/ml2_conf.ini',
        require => Package['neutron']
      }
  }

  neutron::plugins::ml2::driver { $type_drivers:
    flat_networks       => $flat_networks,
    tunnel_id_ranges    => $tunnel_id_ranges,
    network_vlan_ranges => $network_vlan_ranges,
    vni_ranges          => $vni_ranges,
    vxlan_group         => $vxlan_group,
  }

  # Configure ml2_conf.ini
  neutron_plugin_ml2 {
    'ml2/type_drivers':                     value => join($type_drivers, ',');
    'ml2/tenant_network_types':             value => join($tenant_network_types, ',');
    'ml2/mechanism_drivers':                value => join($mechanism_drivers, ',');
    'securitygroup/enable_security_group':  value => $enable_security_group;
  }

  # Specific plugin configuration
  if ('openvswitch' in $mechanism_drivers) {
    if ($::osfamily == 'RedHat') {
      ensure_resource('package', 'neutron-plugin-ovs', {
        ensure => present,
        name   => $::neutron::params::ovs_server_package,
      })
      Package['neutron-plugin-ovs'] -> Neutron_plugin_ovs<||>
    }



    # cylee : move ovs setting to here
    if $enable_tunneling {

        neutron_plugin_ml2 {
            'ovs/enable_tunneling': value => true;
            'ovs/tenant_network_type': value => join($tenant_network_types, ',');
            'ovs/tunnel_types': value => join($tunnel_types, ',');
            'ovs/tunnel_bridge':    value => $tunnel_bridge;
            'ovs/local_ip':         value => $local_ip;
            'ovs/tunnel_id_ranges':  value => $tunnel_id_ranges;
            'ovs/integration_bridge': value => $integration_bridge;
            'agent/polling_interval': value => $polling_interval;
            'agent/tunnel_types': value => join($tunnel_types, ',');
            'agent/l2_population': value => true;
        }
        if 'vxlan' in $tunnel_types {
            validate_vxlan_udp_port($vxlan_udp_port)
            neutron_plugin_ml2 {
                'ovs/vxlan_udp_port': value => $vxlan_udp_port;
            }
        }
    }

    # ----
  }
  if ('linuxbridge' in $mechanism_drivers) {
    if ($::osfamily == 'RedHat') {
      package { 'neutron-plugin-linuxbridge':
        ensure => present,
        name   => $::neutron::params::linuxbridge_server_package,
      }
      Package['neutron-plugin-linuxbridge'] -> Neutron_plugin_linuxbridge<||>
    }
    if ('l2population' in $mechanism_drivers) {
      neutron_plugin_linuxbridge {
        'vxlan/enable_vxlan':  value => true;
        'vxlan/l2_population': value => true;
      }
    } else {
      neutron_plugin_linuxbridge {
        'vxlan/l2_population': value => false;
      }
    }
  }

  if $enable_security_group {
      neutron_plugin_ml2 {
          'securitygroup/firewall_driver': value => $firewall_driver;
      }
  } else {
      neutron_plugin_ml2 {
          'securitygroup/firewall_driver': value => 'neutron.agent.firewall.NoopFirewallDriver';
      }
  }

}
