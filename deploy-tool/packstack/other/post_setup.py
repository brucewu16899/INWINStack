#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import re
import types
#import unittest
#
#class TestPostNic(unittest.TestCase):
#
#    def setUp (self):
#        self.nic_cfg_name = '/tmp/testNIC'
#        f = open(self.nic_cfg_name, 'w')
#        f.close()
#
#    def tearDown (self):
#        os.system('rm -f %s' % self.nic_cfg_name)
#
#    def _create_no_eth_file (self):
#        f = open(self.nic_cfg_name, 'w')
#        f.write( ("# interfaces(5) file used by ifup(8) and ifdown(8)\n"
#                  "auto lo\n"
#                  "iface lo inet loopback"))
#        f.close()
#
#    def _create_eth_file (self, content=None):
#        with open(self.nic_cfg_name, 'w') as f:
#            if content:
#                f.write(content)
#                return
#            else:
#                f.write(("# This file describes the network interfaces available on your system\n"
#                         "# and how to activate them. For more information, see interfaces(5).\n"
#                         "\n"
#                         "# The loopback network interface\n"
#                         "auto lo\n"
#                         "iface lo inet loopback\n"
#                         "# The primary network interface\n"
#                         "auto eth0\n"
#                         "iface eth0 inet static\n"
#                         "        address 192.168.122.90\n"
#                         "        gateway 192.168.122.1\n"
#                         "        dns-nameservers 8.8.8.8 8.8.8.4\n"
#                         "        netmask 255.255.255.0\n"
#                         "\n"
#                         "auto eth1\n"
#                         "iface eth1 inet dhcp"))
#
#
#
#    def _create_no_eth_file_wihtout_permission (self):
#        self._create_no_eth_file()
#        os.system("chmod -r %s" % self.nic_cfg_name)
#
#
#    def test_search_nic_ok(self):
#        self._create_no_eth_file()
#        found_nic = _search_nic("lo", self.nic_cfg_name)
#        self.assertEqual(found_nic, True)
#
#    def test_search_nic_fail(self):
#        self._create_no_eth_file()
#        found_nic = _search_nic("eth0", self.nic_cfg_name)
#        self.assertEqual(found_nic, False)
#
#    def test_search_nic_permission_deny(self):
#        self._create_no_eth_file_wihtout_permission()
#        self.assertRaises(RuntimeError,lambda : _search_nic("lo", self.nic_cfg_name))
#
#    def test_comment_match_block_simple(self):
#        self._create_no_eth_file()
#        comment_result = _comment_match_block("lo", self.nic_cfg_name)
#        expected_content = ("# interfaces(5) file used by ifup(8) and ifdown(8)\n"
#                            "#auto lo\n"
#                            "#iface lo inet loopback")
#        self.assertEqual(comment_result, expected_content)
#
#    def test_comment_match_block_normal(self):
#        expected_content =\
#        ("# This file describes the network interfaces available on your system\n"
#         "# and how to activate them. For more information, see interfaces(5).\n"
#         "\n"
#         "# The loopback network interface\n"
#         "#auto lo\n"
#         "#iface lo inet loopback\n"
#         "# The primary network interface\n"
#         "#auto eth0\n"
#         "#iface eth0 inet static\n"
#         "#        address 192.168.122.90\n"
#         "#        gateway 192.168.122.1\n"
#         "#        dns-nameservers 8.8.8.8 8.8.8.4\n"
#         "#        netmask 255.255.255.0\n"
#         "#\n"
#         "auto eth1\n"
#         "iface eth1 inet dhcp")
#        self._create_eth_file()
#        comment_result = _comment_match_block(["eth0", "lo"],
#                                              self.nic_cfg_name)
#        self.assertEqual(comment_result, expected_content)
#
#    def test_add_eth_promisc_setting(self):
#        src_content = (\
#         "# This file describes the network interfaces available on your system\n"
#         "# and how to activate them. For more information, see interfaces(5).\n"
#         "\n"
#         "# The loopback network interface\n"
#         "#auto lo\n"
#         "#iface lo inet loopback\n"
#         "# The primary network interface\n"
#         "#auto eth0\n"
#         "#iface eth0 inet static\n"
#         "#        address 192.168.122.90\n"
#         "#        gateway 192.168.122.1\n"
#         "#        dns-nameservers 8.8.8.8 8.8.8.4\n"
#         "#        netmask 255.255.255.0\n"
#         "#\n")
#        expected_content =\
#        ("# This file describes the network interfaces available on your system\n"
#         "# and how to activate them. For more information, see interfaces(5).\n"
#         "\n"
#         "# The loopback network interface\n"
#         "#auto lo\n"
#         "#iface lo inet loopback\n"
#         "# The primary network interface\n"
#         "#auto eth0\n"
#         "#iface eth0 inet static\n"
#         "#        address 192.168.122.90\n"
#         "#        gateway 192.168.122.1\n"
#         "#        dns-nameservers 8.8.8.8 8.8.8.4\n"
#         "#        netmask 255.255.255.0\n"
#         "#\n"
#         "auto eth0\n"
#         "iface eth0 inet manual\n"
#         "    up ifconfig $IFACE 0.0.0.0 up\n"
#         "    up ip link set $IFACE promisc on\n"
#         "    down ip link set $IFACE promisc off\n"
#         "    down ifconfig $IFACE down\n"
#         )
#        self._create_eth_file()
#        ret_content = _append_eth_promisc_setting("eth0", src_content)
#        self.assertEqual(ret_content, expected_content)
#
#    def test_append_br_static_promisc_setting(self):
#        src_content = (\
#         "# This file describes the network interfaces available on your system\n"
#         "# and how to activate them. For more information, see interfaces(5).\n"
#         "\n"
#         "# The loopback network interface\n"
#         "#auto lo\n"
#         "#iface lo inet loopback\n"
#         "# The primary network interface\n"
#         "#auto eth0\n"
#         "#iface eth0 inet static\n"
#         "#        address 192.168.122.90\n"
#         "#        gateway 192.168.122.1\n"
#         "#        dns-nameservers 8.8.8.8 8.8.8.4\n"
#         "#        netmask 255.255.255.0\n"
#         "#\n")
#
#        expected_content =\
#        ("# This file describes the network interfaces available on your system\n"
#         "# and how to activate them. For more information, see interfaces(5).\n"
#         "\n"
#         "# The loopback network interface\n"
#         "#auto lo\n"
#         "#iface lo inet loopback\n"
#         "# The primary network interface\n"
#         "#auto eth0\n"
#         "#iface eth0 inet static\n"
#         "#        address 192.168.122.90\n"
#         "#        gateway 192.168.122.1\n"
#         "#        dns-nameservers 8.8.8.8 8.8.8.4\n"
#         "#        netmask 255.255.255.0\n"
#         "#\n"
#         "auto br-ex\n"
#         "iface br-ex inet static\n"
#         "    address 192.168.122.1\n"
#         "    netmask 255.255.255.0\n"
#         "    up ip link set $IFACE promisc on\n"
#         "    down ip link set $IFACE promisc off")
#        ret_content = _append_br_static_promisc_setting("br-ex",
#                                                        "192.168.122.1",
#                                                        "255.255.255.0",
#                                                        src_content)
#        self.assertEqual(ret_content, expected_content)
#
#    def test_append_br_dhcp_promisc_setting(self):
#        src_content = (\
#         "# This file describes the network interfaces available on your system\n"
#         "# and how to activate them. For more information, see interfaces(5).\n"
#         "\n"
#         "# The loopback network interface\n"
#         "#auto lo\n"
#         "#iface lo inet loopback\n"
#         "# The primary network interface\n"
#         "#auto eth0\n"
#         "#iface eth0 inet static\n"
#         "#        address 192.168.122.90\n"
#         "#        gateway 192.168.122.1\n"
#         "#        dns-nameservers 8.8.8.8 8.8.8.4\n"
#         "#        netmask 255.255.255.0\n"
#         "#\n")
#
#        expected_content =\
#        ("# This file describes the network interfaces available on your system\n"
#         "# and how to activate them. For more information, see interfaces(5).\n"
#         "\n"
#         "# The loopback network interface\n"
#         "#auto lo\n"
#         "#iface lo inet loopback\n"
#         "# The primary network interface\n"
#         "#auto eth0\n"
#         "#iface eth0 inet static\n"
#         "#        address 192.168.122.90\n"
#         "#        gateway 192.168.122.1\n"
#         "#        dns-nameservers 8.8.8.8 8.8.8.4\n"
#         "#        netmask 255.255.255.0\n"
#         "#\n"
#         "auto br-ex\n"
#         "iface br-ex inet dhcp\n"
#         "    dns-nameservers 8.8.8.8 8.8.8.4\n"
#         "    netmask 255.255.255.0\n"
#         "    up ip link set $IFACE promisc on\n"
#         "    down ip link set $IFACE promisc off")
#        ret_content = _append_br_dhcp_promisc_setting("br-ex",
#                                                      "255.255.255.0",
#                                                      src_content)
#        self.assertEqual(ret_content, expected_content)

def main():
    post_act("%(CONFIG_EXT_NET_IFACE)s")

def post_act (nic_name):
    os.system("sudo ifdown --exclude=lo -a")
    os.system("sudo ovs-vsctl add-port %(CONFIG_NEUTRON_L3_EXT_BRIDGE)s %s" % nic_name)
    os.system("sudo ifconfig %(CONFIG_NEUTRON_L3_EXT_BRIDGE)s promisc up")
    _search_nic(nic_name, "/etc/network/interfaces")
    content = _comment_match_block([nic_name, "%(CONFIG_NEUTRON_L3_EXT_BRIDGE)s"],
                                   "/etc/network/interfaces")
    content = _append_eth_promisc_setting(nic_name, content)
    if "%(CONFIG_NEUTRON_L3_EXT_BRIDGE_TYPE)s" == "dhcp":
        content = _append_br_dhcp_promisc_setting("%(CONFIG_NEUTRON_L3_EXT_BRIDGE)s",
                                                  "%(CONFIG_EXT_NET_MASK)s",
                                                   content)
    else:
        content = _append_br_static_promisc_setting("%(CONFIG_NEUTRON_L3_EXT_BRIDGE)s",
                                                    "%(CONFIG_NEUTRON_SERVER_HOST)s",
                                                    "%(CONFIG_EXT_NET_MASK)s",
                                                    "%(CONFIG_EXT_NET_GW_IP)s",
                                                    content)

   
    f = open("/tmp/interfaces", "w") 
    f.write(content)
    f.close()
    os.system("sudo mv /etc/network/interfaces /etc/network/interfaces.orig")
    os.system("sudo mv /tmp/interfaces /etc/network/")
    os.system("sudo ifup --exclude=lo -a")

def _search_nic(nic_name, fname):
    found = False
    iface_ptn = re.compile("\s*iface\s+%s\s+" % nic_name)
    try:
        with open(fname, 'r') as in_file:
            for line in in_file:
                if iface_ptn.findall(line):
                    return True

    except IOError as ex:
        raise RuntimeError("interface %s name not found in %s" %\
                           (nic_name, fname))
    return found
    
def _append_eth_promisc_setting(nic_name, src_content):
    
    new_part = ("auto %s\n"
                "iface %s inet manual\n"
                "    up ifconfig $IFACE 0.0.0.0 up\n"
                "    up ip link set $IFACE promisc on\n"
                "    down ip link set $IFACE promisc off\n"
                "    down ifconfig $IFACE down\n") % (nic_name, nic_name)
    return src_content + new_part
            

def _append_br_static_promisc_setting(bridge_name, address, netmask, gateway,
                                      src_content):
    new_part = (\
    "auto %s\n"
    "iface %s inet static\n"
    "    address %s\n"
    "    netmask %s\n"
    "    gateway %s\n"
    "    dns-nameservers 8.8.8.8 8.8.8.4\n"
    "    up ip link set $IFACE promisc on\n"
    "    down ip link set $IFACE promisc off") % (bridge_name, bridge_name,
                                                  address, netmask, gateway)
    return src_content + new_part

def _append_br_dhcp_promisc_setting(bridge_name, netmask, src_content):
    new_part = (\
    "auto %s\n"
    "iface %s inet dhcp\n"
    "    dns-nameservers 8.8.8.8 8.8.8.4\n"
    "    netmask %s\n"
    "    up ip link set $IFACE promisc on\n"
    "    down ip link set $IFACE promisc off") % (bridge_name,
                                                  bridge_name, netmask)
    return src_content + new_part

def _comment_match_block(nic_names, fname):
    if isinstance(nic_names, types.StringTypes):
        nic_names = [nic_names]

    AUTO_PTN = re.compile('^\s*auto\s+%s' % ('|'.join(nic_names)))
    OTHER_AUTO_PTN = re.compile('^\s*auto\s+\w+')
    MATCH_SECT_PTN = re.compile('^\s*mapping|iface\s+%s+\s+' % ('|'.join(nic_names)))
    OTHER_SECT_PTN = re.compile('^\s*mapping|iface\s+\w+')
    COMMENT_PTN = re.compile('^\s*#')
    in_comment_section = False
    output = ""
    comment_line = lambda src : '#%s' % src

    with open(fname, 'r') as fin:
        for line in fin:
            if COMMENT_PTN.findall(line) or line == "":
                output += line
                continue

            if AUTO_PTN.findall(line):
                output += comment_line(line)
                continue
            elif ((not AUTO_PTN.findall(line)) and 
                  (not MATCH_SECT_PTN.findall(line)) and
                  ((not OTHER_AUTO_PTN.findall(line)) and 
                  (not OTHER_SECT_PTN.findall(line))) and
                 in_comment_section):
                output += comment_line(line)
                continue
            elif OTHER_AUTO_PTN.findall(line):
                in_comment_section = False
            elif MATCH_SECT_PTN.findall(line):
                in_comment_section = True
                output += comment_line(line)
                continue

            elif OTHER_SECT_PTN.findall(line):
                in_comment_section = False

            output += line

    return output

if __name__ == "__main__":
#   if len(sys.argv) == 1:
#       unittest.main()
#   else:

    sys.exit(main())

