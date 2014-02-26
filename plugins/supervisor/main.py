from genesis.ui import *
from genesis.com import Plugin, implements
from genesis.api import *
from genesis.utils import *
from genesis import apis

from client import SVClient


class SVPlugin(apis.services.ServiceControlPlugin):
    text = 'Supervisor'
    iconfont = 'gen-bullhorn'
    folder = 'system'

    def on_session_start(self):
        self._client = SVClient(self.app)
        self._tail = None
        self._set = None

    def get_main_ui(self):
        ui = self.app.inflate('supervisor:main')

        if not self._client.test():
            self.put_message('err', 'Supervisor is not running. '
                'Please start it via the Status button to see your tasks.')

        for x in self._client.list():
            ui.append('list', UI.DTR(
                UI.Label(text=x['name']),
                UI.Label(text=x['ptype']),
                UI.Label(text=x['status']),
                UI.Label(text=x['info']),
                UI.HContainer(
                    UI.TipIcon(
                        id='start/'+x['name'],
                        text='Start',
                        iconfont='gen-play-2',
                    ) if x['status'] != 'RUNNING' else None,
                    UI.TipIcon(
                        id='restart/'+x['name'],
                        text='Restart',
                        iconfont='gen-loop-2',
                    ) if x['status'] == 'RUNNING' else None,
                    UI.TipIcon(
                        id='stop/'+x['name'],
                        text='Stop',
                        iconfont='gen-stop',
                    ) if x['status'] == 'RUNNING' else None,
                    UI.TipIcon(
                        id='set/'+x['ptype']+'/'+x['name'],
                        text='Edit',
                        iconfont='gen-pencil',
                    ),
                    UI.TipIcon(
                        id='remove/'+x['name'],
                        text='Remove',
                        iconfont='gen-cancel-circle',
                        warning='Are you sure you want to remove the process %s?'%x['name']
                    ),
                    UI.TipIcon(
                        id='tail/'+x['name'],
                        text='Show logs',
                        iconfont='gen-paste',
                    )
                ),
            ))

        if self._tail:
            ui.append('main', UI.InputBox(
                value=self._client.tail(self._tail),
                hidecancel=True,
                extra='code', id='dlgTail'
            ))

        if self._set and self._set != True:
            ui.find('p%s'%self._set[0]).set('selected', True)
            ui.find('name').set('value', self._set[1])
            ui.find('config').set('value', '\n'.join(['%s = %s' % (x[0], x[1]) for x in self._client.get(self._set[1])]))
        elif not self._set:
            ui.remove('dlgSet')

        return ui

    @event('button/click')
    def on_button(self, event, params, vars=None):
        if params[0] == 'start':
            self._client.start(params[1])
        if params[0] == 'restart':
            self._client.restart(params[1])
        if params[0] == 'stop':
            self._client.stop(params[1])
        if params[0] == 'set':
            if len(params) >= 2:
                self._set = (params[1], params[2])
            else:
                self._set = True
        if params[0] == 'remove':
            self._client.remove(params[1])
        if params[0] == 'tail':
            self._tail = params[1]
        if params[0] == 'refresh':
            self._client.run('reread')

    @event('dialog/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgTail':
            self._tail = None
        elif params[0] == 'dlgSet':
            if vars.getvalue('action', '') == 'OK':
                name = vars.getvalue('name', '')
                ptype = vars.getvalue('ptype', '')
                cfg = vars.getvalue('config', '')
                self._client.set(ptype, name, [x.split(' = ') for x in cfg.split('\n')])
                if self._set and self._set != True and name != self._set[1]:
                    self._client.remove(self._set[1])
            self._set = None


class SVListener(Plugin):
    implements(apis.orders.IListener)
    id = 'supervisor'

    def order(self, op, name, ptype='program', args=[]):
        if op == 'new':
            SVClient(self.app).set(ptype, name, args)
        elif op == 'del':
            SVClient(self.app).remove(name, reread=True)
