An utility to install OpenStack(IceHouse) on **Ubuntu 14.04**.

Our work were based upon PackStack.

--------------------------
 Recommended environment
--------------------------


 -  Ubuntu 14.04 server x86_64
 -  8GB RAM
 -  i5 or above processor
 -  40GB free disk space
 -  1 NIC (for standalone); internet accesability
 -  Select 'basic server install'
 -  Set Language to 'English'
 -  Run 'sudo apt-get update' first before you proceed to next step
 
Only keystone/rabbitmq/postgreSQL/Glance/Nova/Cinder/Neutron/Horizon
pass first round testing.

---------------------------
 Prepare setup environment
---------------------------

Paste below command to shell exclude '$' sign.


::

  $ echo <<EOF > pre-install.sh
  #!/bin/bash
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
  echo 'Please logut and use stack login to install openstack.'
  echo ''
  EOF

::

 $ chmod +x pre-install.sh
 $ sudo ./pre-install.sh
 $ exit

Logout current account and re-login with username 'stack', password 'stack'.

::

 $ sudo apt-get install -y git
 $ git clone --recursive https://github.com/inwin/INWINstack.git
 $ cd INWINstack/deploy-tool/


-----------------------------
 Option 1 (using answer file)
-----------------------------

::

 $ bin/inwinstack --gen-answer-file=ans.txt

then edit ans.txt as appropriate e.g.

 -  Edit the IP address to anywhere you want to install a piece of openstack on another server

::

 $ bin/inwinstack --answer-file=ans.txt

--------------------------------------
 Option 2 Standalone mode(All in one)
--------------------------------------

::

 $ bin/inwinstack --allinone

When setup complete, the installer will generate an packstacXXXXX.txt file under your home folder.

----------
 Logging
----------

The location of the log files and generated puppet manifests are in the
/var/tmp/packstack directory under a directory named by the date in which
packstack was run and a random string (e.g. /var/tmp/packstack/20131022-204316-Bf3Ek2).
Inside, we find a manifest directory and the openstack-setup.log file; puppet
manifests and a log file for each one are found inside the manifest directory.

-----------
 Debugging
-----------

To make packstack write more detailed information into the log file you can use the -d switch:

::

 $ inwinstack -d --allinone

----------------------------
 Using command line utility
----------------------------

When you finish OpenStack installation, the installer will generate two file named with prefix **keystone\_**
Execute below command before you use any OpenStack client utilities.

::

$source keystone_admin  

