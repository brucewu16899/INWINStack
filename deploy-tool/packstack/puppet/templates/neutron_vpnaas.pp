
class { "neutron::agents::vpnaas":
  vpn_device_driver           => 'neutron.services.vpn.device_drivers.ipsec.OpenSwanDriver',
  interface_driver            => 'neutron.agent.linux.interface.OVSInterfaceDriver',
} 
