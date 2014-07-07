from genesis.com import *
from genesis import apis

from backend import FSControl


class POI(object):
    name = ''
    ptype = ''
    path = ''
    icon = ''
    created_by = ''
    remove = True


class POIControl(apis.API):
    def __init__(self, app):
        self.app = app
        if not self.app.session.has_key("pois"):
            self.app.session["pois"] = []
            self.generate_pois()

    def add(self, name, ptype, path, created_by='', icon='gen-folder', remove=True):
        i = POI()
        i.name = name
        i.ptype = ptype
        i.path = path
        i.icon = icon
        i.created_by = created_by
        i.remove = remove
        self.app.session["pois"].append(i)

    def drop(self, poi):
        self.app.session["pois"].remove(poi)

    def drop_by_path(self, path):
        for x in self.app.session["pois"]:
            if x.path == path:
                self.drop(x)

    def get_pois(self):
        return self.app.session["pois"]

    def generate_pois(self):
        self.app.session["pois"] = []
        fs = FSControl(self.app).get_filesystems()
        ws = apis.webapps(self.app).get_sites()
        for x in fs[0]:
            if x.mount and not (x.mount == '/' or x.mount.startswith('/boot')):
                self.add(x.name, 'disk', x.mount, 'filesystems', 'gen-storage', False)
        for x in fs[1]:
            if x.mount and not (x.mount == '/' or x.mount.startswith('/boot')):
                self.add(x.name, 'vdisk', x.mount, 'filesystems', 'gen-storage', False)
        for x in ws:
            if x.stype != 'ReverseProxy':
                self.add(x.name, 'website', x.path, 'webapps',
                    x.sclass.plugin_info.icon if x.sclass and \
                    hasattr(x.sclass.plugin_info, 'iconfont') else 'gen-earth',
                    False
                )
