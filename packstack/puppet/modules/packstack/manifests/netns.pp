#
# Checks if netns is supported and if not updates kernel, iputils
# and iproute

class packstack::netns (
    $warning = "Kernel package with netns support has been installed."
)
{
    if $::netns_support != "true" {
        exec { "netns_dependecy_install":
            path => "/usr/bin/",
            command => "sudo apt-get install -y iputils-* iproute2",
            timeout => 900,
        }

        notify { "packstack_info":
            message => $warning,
            require => Exec["netns_dependecy_install"],
        }
    }
}
