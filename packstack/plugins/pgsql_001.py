"""
Installs and configures PostgreSQL
"""

import uuid
import logging

from packstack.installer import validators
from packstack.installer import utils
from packstack.installer.utils import split_hosts

from packstack.modules.ospluginutils import getManifestTemplate, appendManifestFile

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-PGSQL"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding PostgreSQL OpenStack configuration")
    paramsList = [
                  {"CMD_OPTION"      : "pgsql-host",
                   "USAGE"           : "The IP address of the server on which to install PostgreSQL",
                   "PROMPT"          : "Enter the IP address of the PostgreSQL server",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_ssh],
                   "DEFAULT_VALUE"   : utils.get_localhost_ip(),
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_PGSQL_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "pgsql-user",
                   "USAGE"           : "Username for the PostgreSQL admin user",
                   "PROMPT"          : "Enter the username for the PostgreSQL admin user",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : "postgres",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_PGSQL_USER",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "pgsql-pw",
                   "USAGE"           : "Password for the PostgreSQL admin user",
                   "PROMPT"          : "Enter the password for the PostgreSQL admin user",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_PGSQL_PW",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : True,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "PGSQL",
                  "DESCRIPTION"           : "PostgreSQL Config parameters",
                  "PRE_CONDITION"         : lambda x: 'yes',
                  "PRE_CONDITION_MATCH"   : "yes",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    pgsqlsteps = [
             {'title': 'Adding PostgreSQL manifest entries',
              'functions':[createmanifest]}
    ]
    controller.addSequence("Installing PostgreSQL", [], [], pgsqlsteps)


def createmanifest(config):
    if config['CONFIG_PGSQL_INSTALL'] == 'y':
        install = True
        suffix = 'install'
    else:
        install = False
        suffix = 'noinstall'
        # cylee : if it not going install then just skip it
        return

    # In case we are not installing PostgreSQL server, postgresql* manifests have
    # to be run from Keystone host
    host = install and config['CONFIG_PGSQL_HOST'] \
                    or config['CONFIG_KEYSTONE_HOST']
    manifestfile = "%s_pgsql.pp" % host
    manifestdata = [getManifestTemplate('pgsql_%s.pp' % suffix)]

    def append_for(module, suffix):
        # Modules have to be appended to the existing postgresql.pp
        # otherwise pp will fail for some of them saying that
        # Postgresql::Config definition is missing.
        template = "pgsql_%s_%s.pp" % (module, suffix)
        manifestdata.append(getManifestTemplate(template))


    if (install):
        if (config['CONFIG_PGSQL_HOST']):
            setup_postgres_package(config['CONFIG_PGSQL_HOST'],
                                   "postgresql-common")
        if (config['CONFIG_KEYSTONE_HOST']):
            setup_postgres_python_package([config['CONFIG_KEYSTONE_HOST']])

    # Bevis : 2014.5.16 : disable default install keystone
    append_for("keystone", suffix)
    hosts = set()

    for mod in ['nova', 'cinder', 'glance', 'neutron', 'heat']:
        if config['CONFIG_%s_INSTALL' % mod.upper()] == 'y':
            append_for(mod, suffix)
            
            # Check wich modules are enabled so we can allow their
            # hosts on the firewall
            if mod != 'nova' and mod != 'neutron':
                hosts.add(config.get('CONFIG_%s_HOST' % mod.upper()).strip())
            elif mod == 'neutron':
                hosts.add(config.get('CONFIG_NEUTRON_SERVER_HOST').strip())
            elif config['CONFIG_NOVA_INSTALL'] != 'n':
                #In that remote case that we have lot's of nova hosts
                hosts.add(config.get('CONFIG_NOVA_API_HOST').strip())
                hosts.add(config.get('CONFIG_NOVA_CERT_HOST').strip())
                hosts.add(config.get('CONFIG_NOVA_VNCPROXY_HOST').strip())
                hosts.add(config.get('CONFIG_NOVA_CONDUCTOR_HOST').strip())
                hosts.add(config.get('CONFIG_NOVA_SCHED_HOST').strip())
                if config['CONFIG_NEUTRON_INSTALL'] != 'y':
                    dbhosts = split_hosts(config['CONFIG_NOVA_NETWORK_HOSTS'])
                    hosts |= dbhosts
                for host in config.get('CONFIG_NOVA_COMPUTE_HOSTS').split(','):
                    hosts.add(host.strip())

    if (install):
        setup_postgres_python_package(hosts)

    #disable firewall by bevis - 2014.5.15
#   config['FIREWALL_SERVICE_NAME'] = "postgresql"
#   config['FIREWALL_PORTS'] = "'3306'"
#   config['FIREWALL_CHAIN'] = "INPUT"
#   for host in hosts:
#       config['FIREWALL_ALLOWED'] = "'%s'" % host
#       config['FIREWALL_SERVICE_ID'] = "pgsql_%s" % host
#       manifestdata.append(getManifestTemplate("firewall.pp"))

    appendManifestFile(manifestfile, "\n".join(manifestdata), 'pre')

def setup_postgres_package(host_ip, pkg_name):
    # cylee : 2014-05-19 : Install postgresql relevant package on target host.
    #TODO: It's dirty hack, fix it until puppet execute chain have fix.
    if (host_ip):
        server = utils.ScriptRunner(host_ip)
        server.append("ssh -o StrictHostKeyChecking=no "
                      "-o UserKnownHostsFile=/dev/null "
                      "stack@%s 'sudo apt-get install -y %s'"
                      % (host_ip, pkg_name))
        logging.debug("install package %s in host %s" % (host_ip, pkg_name))
        server.execute()

def setup_postgres_python_package(hosts):
    for host in hosts:
        if host:
            setup_postgres_package(host, "python-psycopg2")
            

