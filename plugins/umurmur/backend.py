import pylibconfig2

from genesis.api import *
from genesis.com import *
from genesis import apis
from genesis.plugins.core.api import ISSLPlugin
from genesis.plugins.users.backend import UsersBackend

arkos_welcome = "Welcome to uMurmur on arkOS!"


class UMurmurConfig(Plugin):
    implements(IConfigurable)
    name = "Murmur"
    id = "umurmur"
    iconfont = "gen-phone"
    service_name = "umurmur"

    def __init__(self):
        self.config_file = self.app.get_config(self).cfg_file
        self.service_mgr = self.app.get_backend(apis.services.IServiceManager)
        self.config = pylibconfig2.Config("")

    def load(self):
        cfg_str = ConfManager.get().load('umurmur', self.config_file)
        try:
            self.config = pylibconfig2.Config(cfg_str)
        except pylibconfig2.PyLibConfigErrors as e:
            self.app.log.error(e)
        if not self.config.lookup('arkos_init'):
            self.config.arkos_init = True
            self.config.welcometext = arkos_welcome

    def save(self):
        running = self.is_service_running()
        if running:
            self.service_mgr.stop(self.service_name)
        ConfManager.get().save("umurmur", self.config_file, str(self.config))
        ConfManager.get().commit("umurmur")
        if running:
            self.service_mgr.start(self.service_name)

    def list_files(self):
        return [self.config_file]

    def is_service_running(self):
        return self.service_mgr.get_status(self.service_name) == "running"


class GeneralConfig(ModuleConfig):
    target = UMurmurConfig
    platform = ['arch', 'arkos']
    labels = {'cfg_file': 'Configuration file'}
    cfg_file = '/etc/umurmur/umurmur.conf'


class UMurmurSSLPlugin(Plugin):
    implements(ISSLPlugin)
    pid = 'umurmur'
    text = "Mumble (VoIP)"
    iconfont = "gen-phone"
    cert_type = 'cert-key'

    def enable_ssl(self, cert, key):
        ub = UsersBackend(self.app)
        ub.add_to_group('umurmur', 'ssl-cert')
        config = UMurmurConfig(self.app)
        config.load()
        config.config.certificate = cert
        config.config.private_key = key
        config.save()

    def disable_ssl(self):
        config = UMurmurConfig(self.app)
        config.load()
        config.config.certificate = "/etc/umurmur/umurmur.cert"
        config.config.private_key = "/etc/umurmur/umurmur.key"
        config.save()
