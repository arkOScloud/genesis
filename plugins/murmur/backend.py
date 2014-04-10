import cStringIO
import configobj

from genesis.api import *
from genesis.com import *
from genesis import apis

orig_welcome = "<br />Welcome to this server running <b>Murmur</b>." \
               "<br />Enjoy your stay!<br />"
new_welcome = "<br />Welcome to this server running <b>Murmur</b> " \
              "on <b>arkOS</b>.<br />Enjoy your stay!<br />"


class MurmurConfig(Plugin):
    implements(IConfigurable)
    name = "Murmur"
    id = "murmur"
    iconfont = "gen-phone"
    service_name = "murmur"

    def __init__(self):
        self.config_file = self.app.get_config(self).cfg_file
        self.config = configobj.ConfigObj()
        self.service_mgr = self.app.get_backend(apis.services.IServiceManager)

    def load(self):
        cfg = ConfManager.get().load('murmur', self.config_file)
        self.config = configobj.ConfigObj(cfg.split("\n"))
        self.rebrand_welcometext()

    def save(self):
        was_running = False
        if self.service_mgr.get_status(self.service_name) == "running":
            was_running = True
            self.service_mgr.stop(self.service_name)
        out = cStringIO.StringIO()
        self.config.write(out)
        ConfManager.get().save("murmur", self.config_file, out.getvalue())
        ConfManager.get().commit("murmur")
        if was_running:
            self.service_mgr.start(self.service_name)

    def get(self, key):
        return self.config[key]

    def set(self, key, value):
        self.config[key] = value

    def items(self):
        return self.config.items()

    def list_files(self):
        return [self.config_file]

    def rebrand_welcometext(self):
        if self.config["welcometext"] in [orig_welcome, ""]:
            self.config["welcometext"] = new_welcome


class GeneralConfig(ModuleConfig):
    target = MurmurConfig
    platform = ['arch', 'arkos']

    labels = {
        'cfg_file': 'Configuration file'
    }

    cfg_file = '/etc/murmur.ini'
