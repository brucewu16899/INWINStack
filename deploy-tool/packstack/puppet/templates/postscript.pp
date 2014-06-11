# 
if '%(CONFIG_NEUTRON_INSTALL)s' == 'y' {
    notice("Grant all icmp/tcp/udp input/output!")

    exec {"fullaccess-rm-sec-group":
        command => "/usr/bin/neutron --os-tenant-name admin --os-username admin --os-password '%(CONFIG_KEYSTONE_ADMIN_PW)s' --os-auth-url='http://%(CONFIG_KEYSTONE_HOST)s:5000/v2.0/' security-group-delete fullaccess",
        onlyif => "/usr/bin/neutron --os-tenant-name admin --os-username admin --os-password '%(CONFIG_KEYSTONE_ADMIN_PW)s' --os-auth-url='http://%(CONFIG_KEYSTONE_HOST)s:5000/v2.0/' security-group-list -F name -f csv |grep fullaccess",
    } ->
    exec {"fullaccess-sec-group":
        command => "/usr/bin/neutron --os-tenant-name admin --os-username admin --os-password '%(CONFIG_KEYSTONE_ADMIN_PW)s' --os-auth-url='http://%(CONFIG_KEYSTONE_HOST)s:5000/v2.0/' security-group-create fullaccess",
    } ->
    exec {"grant-icmp-ingress-sec-group":
        command => "/usr/bin/neutron --os-tenant-name admin --os-username admin --os-password '%(CONFIG_KEYSTONE_ADMIN_PW)s' --os-auth-url='http://%(CONFIG_KEYSTONE_HOST)s:5000/v2.0/' security-group-rule-create --protocol icmp --direction ingress fullaccess",
    } ->
    exec {"grant-icmp-egress-sec-group":
        command => "/usr/bin/neutron --os-tenant-name admin --os-username admin --os-password '%(CONFIG_KEYSTONE_ADMIN_PW)s' --os-auth-url='http://%(CONFIG_KEYSTONE_HOST)s:5000/v2.0/' security-group-rule-create --protocol icmp --direction egress fullaccess",
    } ->
    exec {"grant-tcp-ingress-sec-group":
        command => "/usr/bin/neutron --os-tenant-name admin --os-username admin --os-password '%(CONFIG_KEYSTONE_ADMIN_PW)s' --os-auth-url='http://%(CONFIG_KEYSTONE_HOST)s:5000/v2.0/' security-group-rule-create --protocol tcp --direction ingress fullaccess",
    } ->
    exec {"grant-tcp-egress-sec-group":
        command => "/usr/bin/neutron --os-tenant-name admin --os-username admin --os-password '%(CONFIG_KEYSTONE_ADMIN_PW)s' --os-auth-url='http://%(CONFIG_KEYSTONE_HOST)s:5000/v2.0/' security-group-rule-create --protocol tcp --direction egress fullaccess",
    } ->
    exec {"grant-udp-ingress-sec-group":
        command => "/usr/bin/neutron --os-tenant-name admin --os-username admin --os-password '%(CONFIG_KEYSTONE_ADMIN_PW)s' --os-auth-url='http://%(CONFIG_KEYSTONE_HOST)s:5000/v2.0/' security-group-rule-create --protocol udp --direction ingress fullaccess",
    } ->
    exec {"grant-udp-egress-sec-group":
        command => "/usr/bin/neutron --os-tenant-name admin --os-username admin --os-password '%(CONFIG_KEYSTONE_ADMIN_PW)s' --os-auth-url='http://%(CONFIG_KEYSTONE_HOST)s:5000/v2.0/' security-group-rule-create --protocol udp --direction egress fullaccess",
    }
}

