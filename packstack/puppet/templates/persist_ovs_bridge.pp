if ($::osfamily == 'RedHat'){

    $net_script = "DEVICE=%(CONFIG_NEUTRON_L3_EXT_BRIDGE)s
    DEVICETYPE=ovs
    TYPE=OVSBridge
    BOOTPROTO=static
    IPADDR=$ipaddress_%(EXT_BRIDGE_VAR)s
    NETMASK=$netmask_%(EXT_BRIDGE_VAR)s
    ONBOOT=yes"

    file { "/etc/sysconfig/network-scripts/ifcfg-%(CONFIG_NEUTRON_L3_EXT_BRIDGE)s":
      content => $net_script
    }

} elsif ($::osfamily == 'Debian') {
    # cylee : 
    # variable start with $ipaddress_  or $netmask_ are
    # Puppet facts
    # Please check below link for detail:
    # http://docs.puppetlabs.com/facter/2.0/
    $net_script = "auto %(CONFIG_NEUTRON_L3_EXT_BRIDGE)s
    iface %(CONFIG_NEUTRON_L3_EXT_BRIDGE)s inet static
    address $ipaddress_%(EXT_BRIDGE_VAR)s
    netmask $netmask_%(EXT_BRIDGE_VAR)s"

    file { "/etc/network/interfaces.d/ifcfg-%(CONFIG_NEUTRON_L3_EXT_BRIDGE)s":
      content => $net_script
    }

}
