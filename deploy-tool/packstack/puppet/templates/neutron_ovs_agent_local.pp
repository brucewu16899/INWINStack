class { 'neutron::agents::ovs':
  bridge_mappings => %(CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS)s,
}

file { 'ovs_neutron_plugin.ini':
    path  => '/etc/neutron/plugins/openvswitch/ovs_neutron_plugin.ini',
    #owner => 'root',
    group => 'neutron',
    #Bevis: neutron-ovs-cleanup for RH, disable it.
    #before => Service['neutron-ovs-cleanup'],
    require => Package['neutron-plugin-ovs'],
}
