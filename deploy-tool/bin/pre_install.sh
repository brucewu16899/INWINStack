#!/bin/bash
#
#
#
#
#
#
# Descript:
#    Ths scirpt help you pre-install openstack environment.
#    each node need run it.
# Run:
#   ./pri_install.sh
#
#
#

echo 'Start install...'
echo ''
sudo apt-get install -y python openssh-server sshpass python-netaddr vim man
echo 'stack ALL=(ALL) NOPASSWD:ALL' > /tmp/50_stack_sh
echo 'Defaults:stack !requiretty' >> /tmp/50_stack_sh
sudo chmod 0440 /tmp/50_stack_sh
sudo chown root:root /tmp/50_stack_sh
sudo mv /tmp/50_stack_sh /etc/sudoers.d/50_stack_sh
sudo useradd -m  stack && sudo adduser stack sudo && sudo chsh -s /bin/bash stack
echo "stack:stack" | sudo chpasswd
sudo -u stack /usr/bin/ssh-keygen -t ecdsa -N "" -f /home/stack/.ssh/id_ecdsa
sudo -u stack /usr/bin/ssh-keygen -t rsa -N "" -f /home/stack/.ssh/id_rsa
echo ''
echo ''
echo 'Pre-Install environment complete!'
echo 'Please logout and use stack login to install openstack.'
echo ''