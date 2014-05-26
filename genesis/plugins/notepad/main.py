import os

from genesis.ui import *
from genesis.com import implements
from genesis.api import *
from genesis.utils import shell, enquote, BackgroundProcess
from genesis.plugins.core.api import *
from genesis.utils import *


class NotepadPlugin(CategoryPlugin):
    text = 'Notepad'
    iconfont = 'gen-file-2'
    folder = 'tools'

    def on_session_start(self):
        self._new = None
        self._open = None
        self._roots = []
        self._data = []

    def open(self, path):
        self._tab = len(self._roots)
        self._roots.append(path)
        data = open(path).read()
        self._data.append(data)

    def get_ui(self):
        if not self._roots:
            mui = self.app.inflate('notepad:nofile')
        else:
            mui = self.app.inflate('notepad:main')
            tabs = UI.TabControl(active=self._tab,test='test')
            mui.append('main', tabs)

            idx = 0
            for root in self._roots:
                data = self._data[idx]

                ui = self.app.inflate('notepad:tab')
                tabs.add(root, ui, id=str(idx))

                if root:
                    ui.find('data').set('value', data)
                    ui.find('save').set('action', 'save/%i'%idx)
                    ui.find('data').set('name', 'data/%i'%idx)
                    ui.find('close').set('action', 'close/%i'%idx)
                    ui.find('data').set('id', 'data%i'%idx)

                idx += 1
        if self._new:
            mui.append('main', UI.InputBox(
                text='Enter path for file',
                value='',
                id='dlgNew'
            ))
        if self._open:
            mui.append('main', UI.InputBox(
                text='Enter path for file',
                value='',
                id='dlgOpen'
            ))

        return mui

    @event('button/click')
    def on_button(self, event, params, vars=None):
        if params[0] == 'close':
            self._file = None
        if params[0] == 'new':
            self._new = True
        if params[0] == 'open':
            self._open = True

    @event('form/submit')
    @event('dialog/submit')
    def on_submit(self, event, params, vars=None):
        for x in enumerate(self._roots):
            idx, root = x[0], x[1]
            self._data[idx] = vars.getvalue('data/%i'%idx, None)
            if vars.getvalue('action', None) == 'save/%i'%idx:
                self._tab = idx
                if root is not None:
                    open(root, 'w').write(self._data[idx])
                    self.put_message('info', 'Saved %s'%root)
            elif vars.getvalue('action', '') == 'close/%i'%idx:
                self._tab = 0
                del self._roots[idx]
                del self._data[idx]
        if params[0] == 'frmEdit' and vars.getvalue('action', None) == 'new':
            filename = vars.getvalue('path', '')
            if os.path.exists(filename):
                self.put_message('err', 'That file already exists!')
            elif not os.access(os.path.dirname(filename), os.W_OK):
                self.put_message('err', 'The folder path does not exist.')
            else:
                try:
                    open(filename, 'w')
                    self.open(filename)
                    self.put_message('info', 'File created and opened: %s' % filename)
                except Exception, e:
                    self.put_message('err', 'File creation failed: %s' % str(e))
        elif params[0] == 'frmEdit' and vars.getvalue('action', None) == 'open':
            filename = vars.getvalue('path', '')
            if not os.path.exists(filename):
                self.put_message('err', 'That file does not exist!')
            else:
                self.open(filename)
        elif params[0] == 'dlgNew':
            if vars.getvalue('action', '') == 'OK' and vars.getvalue('value', ''):
                filename = vars.getvalue('value', '')
                if os.path.exists(filename):
                    self.put_message('err', 'That file already exists!')
                elif not os.access(os.path.dirname(filename), os.W_OK):
                    self.put_message('err', 'The folder path does not exist.')
                else:
                    try:
                        open(filename, 'w')
                        self.open(filename)
                        self.put_message('info', 'File created and opened: %s' % filename)
                    except Exception, e:
                        self.put_message('err', 'File creation failed: %s' % str(e))
            self._new = None
        elif params[0] == 'dlgOpen':
            if vars.getvalue('action', '') == 'OK' and vars.getvalue('value', ''):
                filename = vars.getvalue('value', '')
                if not os.path.exists(filename):
                    self.put_message('err', 'That file does not exist!')
                else:
                    self.open(filename)
            self._open = None
