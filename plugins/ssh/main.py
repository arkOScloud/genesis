from genesis.ui import *
from genesis.api import *
from genesis import apis

import backend


class SSHPlugin(apis.services.ServiceControlPlugin):
    text = 'SSH'
    iconfont = 'gen-console'
    folder = 'system'

    def on_init(self):
        ss = backend.SSHConfig(self.app)
        pk = backend.PKeysConfig(self.app)
        self.ssh = ss.read()
        self.pkeys = pk.read()

    def on_session_start(self):
        self._editing = None

    def get_main_ui(self):
        ui = self.app.inflate('ssh:main')
        t = ui.find('list')

        for h in self.pkeys:
            t.append(UI.DTR(
                UI.Label(text=h.type),
                UI.Label(text=h.name),
                UI.HContainer(
                    UI.TipIcon(
                        iconfont='gen-pencil-2',
                        id='edit/' + str(self.pkeys.index(h)),
                        text='Edit'
                    ),
                    UI.TipIcon(
                        iconfont='gen-cancel-circle',
                        id='del/' + str(self.pkeys.index(h)),
                        text='Delete',
                        warning='Remove %s public key'%h.name
                    )
                ),
            ))

        ui.find('root').set('checked', self.ssh['root'])
        ui.find('pkey').set('checked', self.ssh['pkey'])
        ui.find('passwd').set('checked', self.ssh['passwd'])
        ui.find('epasswd').set('checked', self.ssh['epasswd'])

        if self._editing is not None:
            try:
                h = self.pkeys[self._editing]
            except:
                h = backend.PKey()
            wholekey = h.type + ' ' + h.key + ' ' + h.name
            ui.find('dlgEdit').set('value', wholekey)
        else:
            ui.remove('dlgEdit')

        return ui

    @event('button/click')
    def on_click(self, event, params, vars = None):
        if params[0] == 'add':
            self._editing = len(self.pkeys)
        if params[0] == 'edit':
            self._editing = int(params[1])
        if params[0] == 'del':
            self.pkeys.pop(int(params[1]))
            try:
                backend.PKeysConfig(self.app).save(self.pkeys)
            except Exception, e:
                self.put_message('err', 'Failed to save private keys config: %s' % str(e))

    @event('form/submit')
    @event('dialog/submit')
    def on_submit(self, event, params, vars = None):
        if params[0] == 'dlgEdit':
            v = vars.getvalue('value', '')
            if vars.getvalue('action', '') == 'OK':
                h = backend.PKey()
                data = vars.getvalue('value', '').split()
                try:
                    h.type = data[0]
                    h.key = data[1]
                    h.name = data[2]
                except:
                    pass
                try:
                    self.pkeys[self._editing] = h
                except:
                    self.pkeys.append(h)
                try:
                    backend.PKeysConfig(self.app).save(self.pkeys)
                except Exception, e:
                    self.put_message('err', 'Failed to save private keys config: %s' % str(e))
            self._editing = None
        if params[0] == 'frmSSH':
            v = vars.getvalue('value', '')
            if vars.getvalue('action', '') == 'OK':
                self.ssh['root'] = True if vars.getvalue('root', True) is '1' else False
                self.ssh['pkey'] = True if vars.getvalue('pkey', False) is '1' else False
                self.ssh['passwd'] = True if vars.getvalue('passwd', True) is '1' else False
                self.ssh['epasswd'] = True if vars.getvalue('epasswd', False) is '1' else False
                backend.SSHConfig(self.app).save(self.ssh)
                self.put_message('info', 'Saved')
