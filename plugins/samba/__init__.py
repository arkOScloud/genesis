MODULES = ['backend', 'main']

DEPS =  [
    (['any'],
     [
    	('app', 'Samba', 'smbd'),
        ('plugin'),
     ])
]

NAME = 'File Shares (Windows)'
PLATFORMS = ['any']
DESCRIPTION = 'Add, remove and manage Samba (SMB/CIFS) shares'
VERSION = '3'
GENERATION = 1
AUTHOR = 'arkOS'
HOMEPAGE = 'http://ark-os.org'
