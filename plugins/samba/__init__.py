MODULES = ['backend', 'main']

DEPS =  [
    (['any'],
     [
    	('app', 'Samba', 'smbd'),
        ('plugin', 'services'),
     ])
]

NAME = 'File Shares (Windows)'
PLATFORMS = ['any']
DESCRIPTION = 'Add, remove and manage Samba (SMB/CIFS) shares'
VERSION = '2'
GENERATION = 1
AUTHOR = 'arkOS'
HOMEPAGE = 'http://ark-os.org'
