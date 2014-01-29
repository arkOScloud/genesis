# Plugin metadata
NAME = 'Package Manager'
TYPE = 'plugin'
ICON = 'gen-cube'
DESCRIPTION = 'Install, update and remove applications on your system'
CATEGORIES = [
    {
        "primary": "Utilities",
        "secondary": ["Advanced", "Software Management"]
    }
]
VERSION = '5'

AUTHOR = 'arkOS'
HOMEPAGE = 'http://arkos.io'

# Plugin parameters
MODULES = ["api", "main", "component", "pm_apt", "pm_pacman", 
    "pm_portage", "pm_ports", "pm_yum"]
PLATFORMS = ["debian", "arch", "arkos", "freebsd", "centos", 
    "fedora", "gentoo"]
DEPENDENCIES = {
    "debian": [
        {
            "type": "app",
            "name": "dpkg",
            "package": "dpkg",
            "binary": "dpkg"
        }
    ],
    "arch": [
        {
            "type": "app",
            "name": "pacman",
            "package": "pacman",
            "binary": "pacman"
        }
    ],
    "arkos": [
        {
            "type": "app",
            "name": "pacman",
            "package": "pacman",
            "binary": "pacman"
        }
    ],
    "centos": [
        {
            "type": "app",
            "name": "yum",
            "package": "yum",
            "binary": "yum"
        }
    ],
    "fedora": [
        {
            "type": "app",
            "name": "yum",
            "package": "yum",
            "binary": "yum"
        }
    ],
    "freebsd": [
        {
            "type": "app",
            "name": "pkg-tools",
            "package": "pkg-tools",
            "binary": "portupgrade"
        }
    ],
    "gentoo": [
        {
            "type": "app",
            "name": "eix",
            "package": "eix",
            "binary": "eix"
        }
    ]
}
GENERATION = 1
