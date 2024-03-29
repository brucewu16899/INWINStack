# Puppet templating module by James
# Copyright (C) 2012-2013+ James Shubin
# Written by James Shubin <james@shubin.ca>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

class puppet::params::path {

	case $operatingsystem {
		'RedHat', 'CentOS': {
			$manifests = '/etc/puppet/manifests/'
			$hiera = '/etc/puppet/hiera.yaml'
			$hieradata = '/etc/puppet/hieradata/'
			$modules = '/etc/puppet/modules/'
			#$files = '/var/lib/puppet/files/'	# XXX?
			$files = '/etc/puppet/files/'

		}
		'Debian', 'Ubuntu': {
			$manifests = '/etc/puppet/manifests/'
			$modules = '/etc/puppet/modules/'	
			$files = '/etc/puppet/files/'
		}
		default: {
			fail("Operating system: '${operatingsystem}' not supported.")
		}
	}
}

# vim: ts=8
