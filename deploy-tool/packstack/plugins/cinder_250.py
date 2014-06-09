"""
Installs and configures Cinder
"""

import os
import re
import uuid
import logging

from packstack.installer import exceptions
from packstack.installer import processors
from packstack.installer import validators
from packstack.installer.utils import split_hosts

from packstack.installer import basedefs
from packstack.installer import utils

from packstack.modules.shortcuts import get_mq
from packstack.modules.ospluginutils import getManifestTemplate, appendManifestFile
from packstack.installer import exceptions
from packstack.installer import output_messages

# Controller object will
# be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-Cinder"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')

logging.debug("plugin %s loaded", __name__)


def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding OpenStack Cinder configuration")
    paramsList = [
                  {"CMD_OPTION"      : "cinder-host",
                   "USAGE"           : "The IP address of the server on which to install Cinder",
                   "PROMPT"          : "Enter the IP address of the Cinder server",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_ssh],
                   "DEFAULT_VALUE"   : utils.get_localhost_ip(),
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_CINDER_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-db-passwd",
                   "USAGE"           : "The password to use for the Cinder to access DB",
                   "PROMPT"          : "Enter the password for the Cinder DB access",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_CINDER_DB_PW",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : True,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-ks-passwd",
                   "USAGE"           : "The password to use for the Cinder to authenticate with Keystone",
                   "PROMPT"          : "Enter the password for the Cinder Keystone access",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_CINDER_KS_PW",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : True,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-backend",
                   "USAGE"           : ("The Cinder backend to use, valid options are: "
                                        "lvm, gluster, nfs, vmdk"),
                   "PROMPT"          : "Enter the Cinder backend to be configured",
                   "OPTION_LIST"     : ["lvm", "gluster", "nfs", "vmdk"],
                   "VALIDATORS"      : [validators.validate_options],
                   "DEFAULT_VALUE"   : "lvm",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_CINDER_BACKEND",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "CINDER",
                  "DESCRIPTION"           : "Cinder Config parameters",
                  "PRE_CONDITION"         : "CONFIG_CINDER_INSTALL",
                  "PRE_CONDITION_MATCH"   : "y",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)

    def check_lvm_options(config):
        return (config.get('CONFIG_CINDER_INSTALL', 'n') == 'y' and
                config.get('CONFIG_CINDER_BACKEND', 'lvm') == 'lvm')

    paramsList = [
                  {"CMD_OPTION"      : "cinder-volumes-create",
                   "USAGE"           : ("Create Cinder's volumes group. This should only be done for "
                                        "testing on a proof-of-concept installation of Cinder.  This "
                                        "will create a file-backed volume group and is not suitable "
                                        "for production usage."),
                   "PROMPT"          : ("Should Cinder's volumes group be created (for proof-of-concept "
                                        "installation)?"),
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATORS"      : [validators.validate_options],
                   "DEFAULT_VALUE"   : "y",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_CINDER_VOLUMES_CREATE",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "CINDERVOLUMECREATE",
                  "DESCRIPTION"           : "Cinder volume create Config parameters",
                  "PRE_CONDITION"         : check_lvm_options,
                  "PRE_CONDITION_MATCH"   : True,
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)

    def check_lvm_vg_options(config):
        return (config.get('CONFIG_CINDER_INSTALL', 'n') == 'y' and
                config.get('CONFIG_CINDER_BACKEND', 'lvm') == 'lvm' and
                config.get('CONFIG_CINDER_VOLUMES_CREATE', 'y') == 'y')

    paramsList = [
                  {"CMD_OPTION"      : "cinder-volumes-size",
                   "USAGE"           : ("Cinder's volumes group size. Note that actual volume size "
                                        "will be extended with 3% more space for VG metadata."),
                   "PROMPT"          : "Enter Cinder's volumes group usable size",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : "20G",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_CINDER_VOLUMES_SIZE",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "CINDERVOLUMESIZE",
                  "DESCRIPTION"           : "Cinder volume size Config parameters",
                  "PRE_CONDITION"         : check_lvm_vg_options,
                  "PRE_CONDITION_MATCH"   : True,
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)

    def check_gluster_options(config):
        return (config.get('CONFIG_CINDER_INSTALL', 'n') == 'y' and
                config.get('CONFIG_CINDER_BACKEND', 'lvm') == 'gluster')

    paramsList = [
                  {"CMD_OPTION"      : "cinder-gluster-mounts",
                   "USAGE"           : ("A single or comma separated list of gluster volume shares "
                                        "to mount, eg: ip-address:/vol-name, domain:/vol-name "),
                   "PROMPT"          : ("Enter a single or comma separated list of gluster volume "
                                        "shares to use with Cinder"),
                   "OPTION_LIST"     : ["^'([\d]{1,3}\.){3}[\d]{1,3}:/.*'", \
                    "^'[a-zA-Z0-9][\-\.\w]*:/.*'"],
                   "VALIDATORS"      : [validators.validate_multi_regexp],
                   "PROCESSORS"      : [processors.process_add_quotes_around_values],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_CINDER_GLUSTER_MOUNTS",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  ]

    groupDict = { "GROUP_NAME"            : "CINDERGLUSTERMOUNTS",
                  "DESCRIPTION"           : "Cinder gluster Config parameters",
                  "PRE_CONDITION"         : check_gluster_options,
                  "PRE_CONDITION_MATCH"   : True,
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)

    def check_nfs_options(config):
        return (config.get('CONFIG_CINDER_INSTALL', 'n') == 'y' and
                config.get('CONFIG_CINDER_BACKEND', 'lvm') == 'nfs')

    paramsList = [
                  {"CMD_OPTION"      : "cinder-nfs-mounts",
                   "USAGE"           : ("A single or comma seprated list of NFS exports to mount, "
                                        "eg: ip-address:/export-name "),
                   "PROMPT"          : ("Enter a single or comma seprated list of NFS exports to "
                                        "use with Cinder"),
                   "OPTION_LIST"     : ["^'([\d]{1,3}\.){3}[\d]{1,3}:/.*'"],
                   "VALIDATORS"      : [validators.validate_multi_regexp],
                   "PROCESSORS"      : [processors.process_add_quotes_around_values],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_CINDER_NFS_MOUNTS",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  ]

    groupDict = { "GROUP_NAME"            : "CINDERNFSMOUNTS",
                  "DESCRIPTION"           : "Cinder NFS Config parameters",
                  "PRE_CONDITION"         : check_nfs_options,
                  "PRE_CONDITION_MATCH"   : True,
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)

    def check_vcenter_options(config):
        return (config.get('CONFIG_NOVA_INSTALL', 'y') == 'n' and
                config.get('CONFIG_VMWARE_BACKEND', 'n') == 'y' and
                config.get('CONFIG_CINDER_BACKEND', 'lvm') == 'vmdk')

    paramsList = [
                  {"CMD_OPTION"      : "cinder-vcenter-host",
                   "USAGE"           : ("The IP address of the VMware vCenter datastore"),
                   "PROMPT"          : ("Enter the IP address of the VMware vCenter datastore to use with Cinder"),
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_ip],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_VCENTER_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-vcenter-username",
                   "USAGE"           : ("The username to authenticate to VMware vCenter datastore"),
                   "PROMPT"          : ("Enter the username to authenticate on VMware vCenter datastore"),
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_VCENTER_USER",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False,},
                   {"CMD_OPTION"      : "cinder-vcenter-password",
                   "USAGE"           : ("The password to authenticate to VMware vCenter datastore"),
                   "PROMPT"          : ("Enter the password to authenticate on VMware vCenter datastore"),
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : "",
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_VCENTER_PASSWORD",
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False,},
                  ]

    groupDict = { "GROUP_NAME"            : "CINDERVCENTEROPTIONS",
                  "DESCRIPTION"           : "Cinder VMware vCenter Config parameters",
                  "PRE_CONDITION"         : check_vcenter_options,
                  "PRE_CONDITION_MATCH"   : True,
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)

def initSequences(controller):
    if controller.CONF['CONFIG_CINDER_INSTALL'] != 'y':
        return

    cinder_steps = [
             {'title': 'Installing dependencies for Cinder', 'functions':[install_cinder_deps]},
             {'title': 'Adding Cinder Keystone manifest entries', 'functions':[create_keystone_manifest]},
             {'title': 'Adding Cinder manifest entries', 'functions':[create_manifest]}
    ]

    if controller.CONF['CONFIG_CINDER_BACKEND'] == 'lvm':
        cinder_steps.append({'title': 'Checking if the Cinder server has a cinder-volumes vg', 'functions':[check_cinder_vg]})
    controller.addSequence("Installing OpenStack Cinder", [], [], cinder_steps)

def install_cinder_deps(config):
    host = config['CONFIG_CINDER_HOST']
    server = utils.ScriptRunner(host)
    pkgs = []
    backend_pkg_table = { 'lvm' : 'lvm2',
                          'nfs' : 'nfs-common',
                        }
    backend_type = config['CONFIG_CINDER_BACKEND']
    if backend_type in backend_pkg_table:
       pkgs = [backend_pkg_table[backend_type]]

    for p in pkgs:
        server.append("sudo apt-get install -y %(package)s" % dict(package=p))
    server.execute()

def check_cinder_vg(config):
    cinders_volume = 'cinder-volumes'
    cinder_host = config['CONFIG_CINDER_HOST']

    server = utils.ScriptRunner(cinder_host)

    have_cinders_volume = is_cinder_volume_exist(server, cinders_volume)
    server.clear()
    config_lvm_setting(server)


    if config["CONFIG_CINDER_VOLUMES_CREATE"] != "y":
        if not have_cinders_volume:
            raise exceptions.MissingRequirements("The cinder server should"
                " contain a cinder-volumes volume group")
        return

    if have_cinders_volume:
        controller.MESSAGES.append(
            output_messages.INFO_CINDER_VOLUMES_EXISTS)
        return

    server = utils.ScriptRunner(cinder_host)
    # ubuntu use upstart to replace systemd
    rst_cmd = 'restart openstack-cinder-volume'

    server.clear()
    logging.info("A new cinder volumes group will be created")
    err = "Cinder's volume group '%s' could not be created" % \
                        cinders_volume

    cinders_volume_path = '/var/lib/cinder'
    server.append('sudo mkdir -p  %s' % cinders_volume_path)
    logging.debug("Volume's path: %s" % cinders_volume_path)


    cinders_volume_size = get_volume_file_size(
                                config['CONFIG_CINDER_VOLUMES_SIZE'].strip())
    cinders_volume_path = os.path.join(cinders_volume_path, cinders_volume)

    create_new_lvm(cinders_volume, cinders_volume_path, cinders_volume_size,
                   server)
    create_lvm_mount_script(cinders_volume, rst_cmd, cinders_volume_path,
                            server, cinder_host, err)

def is_cinder_volume_exist(server, volume_name):
    # Do we have a cinder-volumes vg?
    have_cinders_volume = False
    
    server.append('sudo vgdisplay %s' % volume_name)
    try:
        server.execute()
        have_cinders_volume = True
    except exceptions.ScriptRuntimeError:
        pass
    return have_cinders_volume

def config_lvm_setting(server):
    """Change target host LVM setting
        snapshot_autoextend_threshold
        snapshot_autoextend_percent
    """

    # Configure system LVM settings (snapshot_autoextend)
    server.append('sudo sed -i -r "s/^ *snapshot_autoextend_threshold +=.*/'
                  '    snapshot_autoextend_threshold = 80/" '
                  '/etc/lvm/lvm.conf')
    server.append('sudo sed -i -r "s/^ *snapshot_autoextend_percent +=.*/'
                  '    snapshot_autoextend_percent = 20/" '
                  '/etc/lvm/lvm.conf')
    try:
        server.execute()
    except exceptions.ScriptRuntimeError:
        logging.info("Warning: Unable to set system LVM settings.")

def get_volume_file_size(volume_size):
    match = re.match('^(?P<size>\d+)G$', volume_size)
    if not match:
        msg = 'Invalid Cinder volumes VG size.'
        raise exceptions.ParamValidationError(msg)

    cinders_volume_size = int(match.group('size')) * 1024
    cinders_reserve = int(cinders_volume_size * 0.03)

    cinders_volume_size = cinders_volume_size + cinders_reserve
    return cinders_volume_size

def create_new_lvm(cinders_volume, cinders_volume_path, cinders_volume_size,
                   server):
    # cylee : 2014-05-23 : file system operation need operate with sudo 
    server.append('sudo dd if=/dev/zero of=%s bs=1 count=0 seek=%sM'
                   % (cinders_volume_path, cinders_volume_size))
    server.append('LOFI=$(sudo losetup --show -f  %s)' % cinders_volume_path)
    server.append('sudo pvcreate $LOFI')
    server.append('sudo vgcreate %s $LOFI' % cinders_volume)

def create_lvm_mount_script(cinders_volume, rst_cmd, cinders_volume_path,
                            server, cinder_host, error_msg):
    # Add the loop device on boot
    server.append('sudo echo "losetup -f %(path)s && '
                        'vgchange -a y %(volume)s && '
                        '%(restart_cmd)s" '
                  '> /tmp/mount-cinder-vol' %
                  {'volume': cinders_volume, 'restart_cmd': rst_cmd,
                   'path': cinders_volume_path})
    server.append('sudo mv /tmp/mount-cinder-vol /etc/init.d/')
    server.append('sudo ln -sf /etc/init.d/mount-cinder-vol'
                  ' /etc/rcS.d/S59mount-cinder-vol')
    server.append('sudo chmod +x /etc/init.d/mount-cinder-vol')

    # Let's make sure it exists
    server.append('sudo vgdisplay %s' % cinders_volume)

    try:
        server.execute()
    except exceptions.ScriptRuntimeError:
        # Release loop device if cinder's volume creation
        # fails.
        try:
            logging.debug("Release loop device, volume creation failed")
            server = utils.ScriptRunner(controller.CONF['CONFIG_CINDER_HOST'])
            server.append('sudo losetup -d $(losetup -j %s | cut -d : -f 1)' %
                           cinders_volume_path
            )
            server.execute()
        except:
            pass

        raise exceptions.MissingRequirements(error_msg)

def create_keystone_manifest(config):
    manifestfile = "%s_keystone.pp" % controller.CONF['CONFIG_KEYSTONE_HOST']
    manifestdata = getManifestTemplate("keystone_cinder.pp")
    appendManifestFile(manifestfile, manifestdata)


def create_manifest(config):
    manifestdata = getManifestTemplate(get_mq(config, "cinder"))
    manifestfile = "%s_cinder.pp" % controller.CONF['CONFIG_CINDER_HOST']
    manifestdata += getManifestTemplate("cinder.pp")

    if config['CONFIG_CINDER_BACKEND'].lower() == "lvm":
        manifestdata += getManifestTemplate("cinder_lvm.pp")
    if config['CONFIG_CINDER_BACKEND'] == "gluster":
        manifestdata += getManifestTemplate("cinder_gluster.pp")
    if config['CONFIG_CINDER_BACKEND'] == "nfs":
        manifestdata += getManifestTemplate("cinder_nfs.pp")
    if config['CONFIG_CINDER_BACKEND'] == "vmdk":
        manifestdata += getManifestTemplate("cinder_vmdk.pp")
    if config['CONFIG_CEILOMETER_INSTALL'] == 'y':
        manifestdata += getManifestTemplate('cinder_ceilometer.pp')
    if config['CONFIG_SWIFT_INSTALL'] == 'y':
        config['CONFIG_SWIFT_PROXY'] = config['CONFIG_SWIFT_PROXY_HOSTS'].split(',')[0].strip()
        manifestdata += getManifestTemplate('cinder_backup.pp')

#   config['FIREWALL_SERVICE_NAME'] = "cinder"
#   config['FIREWALL_PORTS'] = "'3260', '8776'"
#   config['FIREWALL_CHAIN'] = "INPUT"
#
#   if config['CONFIG_NOVA_INSTALL'] == 'y':
#       for host in split_hosts(config['CONFIG_NOVA_COMPUTE_HOSTS']):
#           config['FIREWALL_ALLOWED'] = "'%s'" % host
#           config['FIREWALL_SERVICE_ID'] = "cinder_%s" % host
#           manifestdata += getManifestTemplate("firewall.pp")
#   else:
#       config['FIREWALL_ALLOWED'] = "'ALL'"
#       config['FIREWALL_SERVICE_ID'] = "cinder_ALL"
#       manifestdata += getManifestTemplate("firewall.pp")

    appendManifestFile(manifestfile, manifestdata)
