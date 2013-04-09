import os
from genesis.utils import hashpw, shell
from ConfigParser import ConfigParser


RCFG_FILE = '/root/genesis-re.conf'

def reconfigure(cfg):
    if not os.path.exists(RCFG_FILE):
        return

    rcfg = ConfigParser()
    rcfg.read(RCFG_FILE)

    if rcfg.has_option('genesis', 'credentials'):
        u,p = rcfg.get('genesis', 'credentials').split(':')
        cfg.remove_option('users', 'admin')
        if not p.startswith('{SHA}'):
            p = hashpw(p)
        cfg.set('users', u, p)

    if rcfg.has_option('genesis', 'plugins'):
        for x in rcfg.get('genesis', 'plugins').split():
            shell('genesis-pkg get ' + x)

    if rcfg.has_option('genesis', 'ssl'):
        c,k = rcfg.get('genesis', 'ssl').split()
        cfg.set('ssl', '1')
        cfg.set('cert_key', k)
        cfg.set('cert_file', c)

    if rcfg.has_option('genesis', 'port'):
        cfg.set('genesis', 'bind_port', rcfg.get('genesis', 'port'))

    if rcfg.has_option('genesis', 'host'):
        cfg.set('genesis', 'bind_host', rcfg.get('genesis', 'host'))

    cfg.set('genesis', 'firstrun', 'no')
    cfg.save()
    os.unlink(RCFG_FILE)
