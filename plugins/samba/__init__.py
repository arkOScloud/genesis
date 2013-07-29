MODULES = ['backend', 'main']

DEPS =  [
    (['any'],
     [
    	('app', 'samba', 'smbd'),
        ('plugin'),
     ])
]

NAME = 'File Shares (Windows)'
ICON = 'gen-upload-2'
PLATFORMS = ['any']
DESCRIPTION = 'Add, remove and manage Samba (SMB/CIFS) shares'
VERSION = '4'
GENERATION = 1
AUTHOR = 'arkOS'
HOMEPAGE = 'http://arkos.io'
