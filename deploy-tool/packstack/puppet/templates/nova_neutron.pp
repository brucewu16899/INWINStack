
class {"nova::network::neutron":
  neutron_admin_password => "%(CONFIG_NEUTRON_KS_PW)s",
  neutron_auth_strategy => "keystone",
  neutron_url => "http://%(CONFIG_NEUTRON_SERVER_HOST)s:9696",
  neutron_admin_tenant_name => "services",
  neutron_admin_auth_url => "http://%(CONFIG_KEYSTONE_HOST)s:35357/v2.0",
  # cylee : Check out http://kashyapc.fedorapeople.org/virt/openstack/rdo/IceHouse-Nova-Neutron-ML2-GRE-OVS.txt
  vif_plugging_is_fatal => false,
  vif_plugging_timeout  => 0,
}

class {"nova::compute::neutron":
  libvirt_vif_driver => "%(CONFIG_NOVA_LIBVIRT_VIF_DRIVER)s",
}
