# Plugin metadata
NAME = 'Secure Shell (SSH)'
TYPE = 'plugin'
ICON = 'gen-console'
DESCRIPTION = 'Change SSH settings and manage public keys'
CATEGORIES = [
    {
        "primary": "Utilities",
        "secondary": ["Advanced", "Command line (CLI)", 
            "Remote Management"]
    }
]
VERSION = '3'

AUTHOR = 'arkOS'
HOMEPAGE = 'http://arkos.io'
APP_AUTHOR = "OpenSSH"
APP_HOMEPAGE = "http://www.openssh.com/"
LOGO = False

SERVICES = [
    {
        "name": "SSH Server",
        "binary": "sshd",
        "ports": [('tcp', '22')]
    }
]

F2B = [
    {
        "name": "sshd"
    }
]

# Plugin parameters
MODULES = ["main", "backend"]
PLATFORMS = ["any"]
DEPENDENCIES = {
    "any": [
        {
            "type": "app",
            "name": "OpenSSH",
            "package": "openssh",
            "binary": "sshd"
        }
    ]
}
GENERATION = 1
