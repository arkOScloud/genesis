from genesis.api import *
from genesis import apis
from genesis.com import *
from genesis.utils import *
from genesis.plugins.users.backend import UsersBackend

import base64
import hashlib
import lxml.etree as ET
import OpenSSL
import os
import pwd
import shutil


class SyncthingConfig(Plugin):
    implements(IConfigurable)
    name = 'Syncthing'
    id = 'syncthing'
    iconfont = 'gen-loop-2'

    def load(self):
        self.mgr = self.app.get_backend(apis.services.IServiceManager)
        data = ConfManager.get().load('syncthing', self.configFile)
        parser = ET.XMLParser(remove_blank_text=True)
        self.config = ET.fromstring(data, parser) if data else None
        self.myid = self.getmyid()

    def save(self, reload=True):
        wasrunning = False
        if reload and self.mgr.get_status('syncthing@syncthing') == 'running':
            wasrunning = True
        ConfManager.get().save('syncthing', self.configFile, ET.tostring(self.config, pretty_print=True))
        ConfManager.get().commit('syncthing')
        if wasrunning and reload:
            self.mgr.restart('syncthing@syncthing')

    def __init__(self):
        self.configDir = '/home/syncthing/.config/syncthing'
        self.configFile = os.path.join(self.configDir, 'config.xml')
        if not os.path.exists(self.configFile):
            if not os.path.exists(self.configDir):
                UsersBackend(self.app).add_sys_with_home('syncthing')
                os.makedirs(self.configDir)
                uid = pwd.getpwnam('syncthing').pw_uid
                for r, d, f in os.walk('/home/syncthing'):
                    for x in d:
                        os.chown(os.path.join(r, x), uid, -1)
                    for x in f:
                        os.chown(os.path.join(r, x), uid, -1)
            self.app.get_backend(apis.services.IServiceManager).real_restart('syncthing@syncthing')
        self.config = None

    def list_files(self):
        return [self.configFile]

    def getopt(self, opt):
        return self.config.find("./options/%s" % opt).text

    def setopt(self, opt, value):
        self.config.find("./options/%s" % opt).text = value

    def getmyid(self):
        if not os.path.exists(os.path.join(self.configDir, 'cert.pem')):
            return None
        c = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM,
            open(os.path.join(self.configDir, 'cert.pem'), 'r').read())
        s = hashlib.sha256()
        s.update(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_ASN1, c))
        b = base64.b32encode(s.digest()).rstrip('=')
        return b


class SyncthingControl(Plugin):
    def __init__(self):
        super(Plugin, self).__init__()
        self.cfg = SyncthingConfig(self.app)

    def add_repo(self, name, dir, ro, perms, vers, nids=[]):
        e = ET.Element('repository', {"id": name, "directory": dir,
            "ro": "true" if ro else "false", 
            "ignorePerms": "true" if perms else "false"})
        for x in nids:
            nid = self.cfg.config.find("./node[@name='%s']" % x)
            e.append(ET.Element('node', {"id": nid.attrib['id']}))
        v = ET.Element('versioning')
        if vers:
            v.set("type", "simple")
            v.append(ET.Element('param', {"key": "keep", "val": vers}))
        e.append(v)
        e.append(ET.Element('syncorder'))
        self.cfg.config.find('.').append(e)
        self.cfg.save()
        if not os.path.exists(dir):
            if dir.startswith('~'):
                dir = os.path.join(os.path.expanduser("~syncthing"), dir.lstrip("~/"))
            os.makedirs(dir)
        uid = pwd.getpwnam('syncthing').pw_uid
        for r, d, f in os.walk(dir):
            for x in d:
                os.chown(os.path.join(r, x), uid, -1)
            for x in f:
                os.chown(os.path.join(r, x), uid, -1)

    def edit_repo(self, name, dir, ro, perms, vers, nids=[]):
        e = self.cfg.config.find("./repository[@id='%s']" % name)
        e.set('directory', dir)
        e.set('ro', "true" if ro else "false")
        e.set('ignorePerms', "true" if perms else "false")
        for x in nids:
            nid = self.cfg.config.find("./node[@name='%s']" % x)
            e.append(ET.Element('node', {"id": nid.attrib['id']}))
        v = e.find("versioning")
        if vers and v.find("param"):
            v.find("param").set("val", vers)
        elif vers:
            v.set("type", "simple")
            v.append(ET.Element('param', {"key": "keep", "val": vers}))
        elif v.find("param"):
            if v.has_key("type"):
                del v.attrib["type"]
            v.remove(v.find("param"))
        self.cfg.save()

    def del_repo(self, name, rmfol=False):
        dir = self.cfg.config.find("./repository[@id='%s']" % name).attrib["directory"]
        self.cfg.config.remove(self.cfg.config.find("./repository[@id='%s']" % name))
        self.cfg.save()
        if rmfol:
            shutil.rmtree(dir)

    def get_repos(self):
        r = []
        try:
            for x in self.cfg.config.findall("./repository"):
                r.append({"id": x.attrib["id"], "directory": x.attrib["directory"],
                    "ro": x.attrib["ro"]=="true", "ignorePerms": x.attrib["ignorePerms"]=="true",
                    "nodes": [y.attrib["id"] for y in x.findall("node")],
                    "versioning": x.find("versioning/param").attrib["val"] if x.find("versioning/param") else False
                    })
        except AttributeError:
            pass
        return r

    def add_node(self, name, id, addr):
        e = ET.Element('node', {"id": id.replace("-", ""), "name": name})
        a = ET.Element('address')
        a.text = addr
        e.append(a)
        self.cfg.config.find('.').append(e)
        self.cfg.save()

    def edit_node(self, name, newname):
        e = self.cfg.config.find("./node[@name='%s']" % name)
        e.set("name", newname)
        self.cfg.save()

    def del_node(self, name):
        self.cfg.config.remove(self.cfg.config.find("./node[@name='%s']" % name))
        self.cfg.save()

    def get_nodes(self):
        r = []
        try:
            for x in self.cfg.config.findall("./node"):
                r.append({"id": x.attrib["id"], "name": x.attrib["name"],
                    "address": x.find("address").text, 
                    "myid": x.attrib["id"]==self.cfg.myid})
        except AttributeError:
            pass
        return r
