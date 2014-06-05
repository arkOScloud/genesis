import os

from genesis.ui import *
from genesis.api import *
from genesis.utils import *
from genesis import apis
from genesis.plugins.network.backend import IHostnameManager

from backend import SSControl


class SSPlugin(CategoryPlugin):
    text = 'SparkleShare'
    iconfont = 'gen-upload-2'
    folder = 'servers'

    def on_session_start(self):
        self._hostname = self.app.get_backend(IHostnameManager).gethostname().lower()
        self._sc = SSControl(self.app)
        self._add, self._link = None, None

    def get_ui(self):
        if not os.path.exists('/home/sparkleshare'):
            os.makedirs('/home/sparkleshare')
            
        ui = self.app.inflate('sparkleshare:main')

        for x in self._sc.get_projects():
            ui.append('list', UI.DTR(
                UI.Label(text=x),
                UI.Label(text='ssh://sparkleshare@%s'%self._hostname),
                UI.Label(text=os.path.join('/home/sparkleshare', x)),
                UI.HContainer(
                    UI.TipIcon(
                        id='remove/'+x,
                        text='Remove',
                        iconfont='gen-cancel-circle',
                        warning='Are you sure you want to remove the %s project?'%x
                    )
                ),
            ))

        if self._add:
            ui.append('main', UI.DialogBox(
                UI.FormLine(
                    UI.TextInput(name='name'),
                    text='Project name'
                ),
                UI.FormLine(
                    UI.Checkbox(name='crypt'),
                    text='Encrypted?'
                ),
                id='dlgAdd'
            ))

        if self._link:
            ui.append('main', UI.InputBox(
                text='Paste your Client ID', id='dlgLink'
            ))

        return ui

    @event('button/click')
    def on_button(self, event, params, vars=None):
        if params[0] == 'add':
            self._add = True
        if params[0] == 'link':
            self._link = True
        if params[0] == 'remove':
            self._sc.del_project(params[1])
            self.put_message('success', 'Project deleted successfully')

    @event('dialog/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgAdd':
            if vars.getvalue('action', '') == 'OK':
                name = vars.getvalue('name', '')
                p = self._sc.get_projects()
                if not name:
                    self.put_message('err', 'You must choose a project name')
                elif name in p or name+'-crypto' in p:
                    self.put_message('err', 'You already have a project with this name!')
                else:
                    try:
                        self._sc.add_project(name, crypto=vars.getvalue('crypt', '')=='1')
                        self.put_message('success', 'Project created successfully')
                    except Exception, e:
                        self.put_message('err', str(e))
            self._add = None
        elif params[0] == 'dlgLink':
            if vars.getvalue('action', '') == 'OK' and vars.getvalue('value', ''):
                self._sc.link_client(vars.getvalue('value'))
            self._link = None
