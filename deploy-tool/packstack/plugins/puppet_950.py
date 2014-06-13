# -*- coding: utf-8 -*-

"""
Installs and configures puppet
"""
import sys
import logging
import os
import platform
import time

from packstack.installer import utils
from packstack.installer import basedefs, output_messages
from packstack.installer.exceptions import ScriptRuntimeError, PuppetError

from packstack.modules.common import filtered_hosts
from packstack.modules.ospluginutils import manifestfiles
from packstack.modules.puppet import scan_logfile, validate_logfile

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OSPUPPET"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')

logging.debug("plugin %s loaded", __name__)

CURR_DIR = os.path.dirname(__file__)
MODULE_DIR = os.path.abspath(os.path.normpath(os.path.join(CURR_DIR,
                                              "../puppet/modules/")))

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding OpenStack Puppet configuration")
    paramsList = [
                 ]

    groupDict = {"GROUP_NAME"            : "PUPPET",
                 "DESCRIPTION"           : "Puppet Config parameters",
                 "PRE_CONDITION"         : lambda x: 'yes',
                 "PRE_CONDITION_MATCH"   : "yes",
                 "POST_CONDITION"        : False,
                 "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    puppetpresteps = [
             {'title': 'Clean Up', 'functions':[runCleanup]},
    ]
    controller.insertSequence("Clean Up", [], [], puppetpresteps, index=0)

    puppetsteps = [
        {'title': 'Installing Dependencies',
            'functions': [installdeps]},
        {'title': 'Copying Puppet modules and manifests',
            'functions': [copyPuppetModules]},
        {'title': 'Applying Puppet manifests',
            'functions': [applyPuppetManifest]},
        {'title': 'Create demo network',
            'functions': [init_demo_network]},
    ]
    controller.addSequence("Puppet", [], [], puppetsteps)


def runCleanup(config):
    localserver = utils.ScriptRunner()
    localserver.append("rm -rf %s/*pp" % basedefs.PUPPET_MANIFEST_DIR)
    localserver.execute()


def installdeps(config):
    for hostname in filtered_hosts(config):
        server = utils.ScriptRunner(hostname)
        # cylee : 2014-05-13 : change install package name for Ubuntu
        for package in ("puppet",
                        "openssh-client", "tar", "netcat"):
            server.append("sudo -u root apt-get install -y %s" % (package))
        server.execute()


def copyPuppetModules(config):
    os_modules = ' '.join(('apache', 'ceilometer', 'certmonger', 'cinder',
                           'concat', 'firewall', 'glance', 'heat', 'horizon',
                           'inifile', 'keystone', 'memcached', 'mongodb',
                           'mysql', 'neutron', 'nova', 'nssdb', 'openstack',
                           'packstack', 'qpid', 'rabbitmq', 'rsync', 'ssh', 'stdlib',
                           'swift', 'sysctl', 'tempest', 'vcsrepo', 'vlan',
                           'vswitch', 'xinetd', 'postgresql', 'staging', 'apt'))

    # write puppet manifest to disk
    manifestfiles.writeManifests()


    server = utils.ScriptRunner()
    # cylee : Each system must create an sudoer called 'stack',
    #         it don't need password while sudo.
    for hostname in filtered_hosts(config):
        host_dir = config['HOST_DETAILS'][hostname]['tmpdir']
        # copy Packstack manifests
        server.append("cd %s/puppet" % basedefs.DIR_PROJECT_DIR)
        server.append("cd %s" % basedefs.PUPPET_MANIFEST_DIR)
        server.append("tar --dereference -cpzf - ../manifests | "
                      "ssh -o StrictHostKeyChecking=no "
                          "-o UserKnownHostsFile=/dev/null "
                          "stack@%s tar -C %s -xpzf -" % (hostname, host_dir))
                
        server.append("cd %s/" % basedefs.DIR_PROJECT_DIR)
        server.append("tar --dereference -cpzf - other | "
                      "ssh -o StrictHostKeyChecking=no "
                          "-o UserKnownHostsFile=/dev/null "
                          "stack@%s tar -C %s -xpzf -" % (hostname, host_dir))

        # copy resources
        for path, localname in controller.resources.get(hostname, []):
            server.append("scp -o StrictHostKeyChecking=no "
                "-o UserKnownHostsFile=/dev/null %s stack@%s:%s/resources/%s" %
                (path, hostname, host_dir, localname))

        # copy Puppet modules required by Packstack
        server.append("cd %s" % MODULE_DIR)
        server.append("tar --dereference -cpzf - %s | "
                      "ssh -o StrictHostKeyChecking=no "
                          "-o UserKnownHostsFile=/dev/null "
                          "stack@%s tar -C %s -xpzf -" %
                      (os_modules, hostname, os.path.join(host_dir, 'modules')))
    server.execute()


def waitforpuppet(currently_running):
    global controller
    log_len = 0
    twirl = ["*  ","** ","***","** "]
    while currently_running:
        for hostname, finished_logfile in currently_running:
            log_file = os.path.splitext(os.path.basename(finished_logfile))[0]
            if len(log_file) > log_len:
                log_len = len(log_file)
            if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
                twirl = twirl[-1:] + twirl[:-1]
                sys.stdout.write(("\rTesting if puppet apply is finished: %s" % log_file).ljust(40 + log_len))
                sys.stdout.write("[ %s ]" % twirl[0])
                sys.stdout.flush()
            try:
                # Once a remote puppet run has finished, we retrieve the log
                # file and check it for errors
                local_server = utils.ScriptRunner()
                log = os.path.join(basedefs.PUPPET_MANIFEST_DIR,
                                   os.path.basename(finished_logfile).replace(".finished", ".log"))
                local_server.append('scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null stack@%s:%s %s' % (hostname, finished_logfile, log))
                # To not pollute logs we turn of logging of command execution
                local_server.execute(log=False)

                # If we got to this point the puppet apply has finished
                currently_running.remove((hostname, finished_logfile))

                # clean off the last "testing apply" msg
                if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
                    sys.stdout.write(('\r').ljust(45 + log_len))

            except ScriptRuntimeError:
                # the test raises an exception if the file doesn't exist yet
                # TO-DO: We need to start testing 'e' for unexpected exceptions
                time.sleep(0.5)
                continue

            # check log file for relevant notices
            controller.MESSAGES.extend(scan_logfile(log))

            # check the log file for errors
            sys.stdout.write('\r')
            try:
                validate_logfile(log)
                state = utils.state_message('%s:' % log_file, 'DONE', 'green')
                sys.stdout.write('%s\n' % state)
                sys.stdout.flush()
            except PuppetError:
                state = utils.state_message('%s:' % log_file, 'ERROR', 'red')
                sys.stdout.write('%s\n' % state)
                sys.stdout.flush()
                raise


def applyPuppetManifest(config):
    if config.get("DRY_RUN"):
        return
    currently_running = []
    lastmarker = None
    loglevel = ''
    logcmd = False
    if logging.root.level <= logging.DEBUG:
        loglevel = '--debug'
        logcmd = True
    for manifest, marker in manifestfiles.getFiles():
        # if the marker has changed then we don't want to proceed until
        # all of the previous puppet runs have finished
        if lastmarker != None and lastmarker != marker:
            waitforpuppet(currently_running)
        lastmarker = marker

        for hostname in filtered_hosts(config):
            if "%s_" % hostname not in manifest:
                continue

            host_dir = config['HOST_DETAILS'][hostname]['tmpdir']
            print "Applying %s" % manifest
            server = utils.ScriptRunner(hostname)

            man_path = os.path.join(config['HOST_DETAILS'][hostname]['tmpdir'],
                                    basedefs.PUPPET_MANIFEST_RELATIVE,
                                    manifest)

            running_logfile = "%s.running" % man_path
            finished_logfile = "%s.finished" % man_path
            currently_running.append((hostname, finished_logfile))
            # The apache puppet module doesn't work if we set FACTERLIB
            # https://github.com/puppetlabs/puppetlabs-apache/pull/138
            if not (manifest.endswith('_horizon.pp') or manifest.endswith('_nagios.pp')):
                server.append("export FACTERLIB=$FACTERLIB:%s/facts" % host_dir)
            server.append("touch %s" % running_logfile)
            server.append("chmod 600 %s" % running_logfile)
            server.append("export PACKSTACK_VAR_DIR=%s" % host_dir)
            # cylee : Apply patch should run with sudo
            command = ("( flock %s/ps.lock sudo puppet apply"
                       " --profile --debug --verbose " 
                       "%s --modulepath %s/modules %s > %s 2>&1 < /dev/null ;" 
                       " mv %s %s ) > /dev/null 2>&1 < /dev/null &")\
                       % (host_dir, loglevel, host_dir, man_path,
                          running_logfile, running_logfile, finished_logfile)

            server.append(command)
            server.execute(log=logcmd)

    # wait for outstanding puppet runs befor exiting
    waitforpuppet(currently_running)

def init_demo_network(config):
    def _build_network_script(cfg):
        with open("%s/other/default-network.sh.template" % basedefs.DIR_PROJECT_DIR, 'r') as f:
            return f.read() % cfg

    host = config['CONFIG_KEYSTONE_HOST']
    content = _build_network_script(config)
    script_file = open("/tmp/create-net-script.sh", "w")
    script_file.write(content)
    script_file.close()
    os.system("chmod +x /tmp/create-net-script.sh")
    os.system("scp /tmp/create-net-script.sh stack@%s:/tmp/" % host)
    os.system("scp $HOME/keystonerc_admin stack@%s:/tmp/" % host)
    server = utils.ScriptRunner(host)
    server.append("cd /tmp/ && /tmp/create-net-script.sh")
    server.execute()






