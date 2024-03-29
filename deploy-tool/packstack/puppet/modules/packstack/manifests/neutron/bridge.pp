
# Loads bridge modules and sets appropriate sysctl.conf variables

class packstack::neutron::bridge {
    if( $::osfamily == 'Redhat' ) {
        file { 'bridge-module-loader':
            path => '/etc/sysconfig/modules/openstack-neutron.modules',
            ensure => present,
            mode => 0700,
            content => template('packstack/openstack-neutron.modules.erb'),
        }
    } elsif ( $::osfamily == 'Debian' ) {
        # Put linux bridge to blacklist
        file { 'bridge-module-loader':
            path => '/etc/modprobe.d/openstack-neutron-blacklist.conf',
            ensure => present,
            mode => 0644,
            content => template('packstack/openstack-neutron-blacklist.conf.erb'),
        }
    }

    file_line { '/etc/sysctl.conf bridge-nf-call-ip6tables':
        path  => '/etc/sysctl.conf',
        line  => 'net.bridge.bridge-nf-call-ip6tables=1',
        match => 'net.bridge.bridge-nf-call-ip6tables\s*=',
    } -> file_line { '/etc/sysctl.conf bridge-nf-call-iptables':
        path  => '/etc/sysctl.conf',
        line  => 'net.bridge.bridge-nf-call-iptables=1',
        match => 'net.bridge.bridge-nf-call-iptables\s*=',
    } -> file_line { '/etc/sysctl.conf bridge-nf-call-arptables':
        path  => '/etc/sysctl.conf',
        line  => 'net.bridge.bridge-nf-call-arptables=1',
        match => 'net.bridge.bridge-nf-call-arptables\s*=',
    }
}
