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
        self._roots = []
        self._files = []
        self._data = []

    def add_tab(self):
        self._tab = len(self._roots)
        self._roots.append('')
        self._files.append(None)
        self._data.append(None)

    def open(self, path):
        self.add_tab()
        data = open(path).read()
        self._files[self._tab] = path
        self._data[self._tab] = data

    def get_ui(self):
        if not self._roots:
            mui = self.app.inflate('notepad:nofile')
        else:
            mui = self.app.inflate('notepad:main')
            tabs = UI.TabControl(active=self._tab,test='test')
            mui.append('main', tabs)

            idx = 0
            for root in self._roots:
                file = self._files[idx]
                data = self._data[idx]

                ui = self.app.inflate('notepad:tab')
                tabs.add(file or root, ui, id=str(idx))

                ui.find('data').set('name', 'data/%i'%idx)
                if file is not None:
                    ui.find('data').set('value', data)
                ui.find('data').set('id', 'data%i'%idx)

                if not file:
                    ui.remove('save')
                    if len(self._roots) == 1:
                        ui.remove('close')

                idx += 1

            tabs.add("+", None, id='newtab', form='frmEdit')
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
        if params[0] == 'btnClose':
            self._file = None
        if params[0] == 'newtab':
            self.add_tab()
        if params[0] == 'new':
            self._new = True
        if params[0] == 'save':
            if self._files[self._tab] is not None:
                open(self._files[self._tab], 'w').write(self._data[self._tab])
                self.put_message('info', 'Saved %s'%self._files[self._tab])
        if params[0] == 'close':
            self._tab = 0
            del self._roots[int(params[1])]
            del self._files[int(params[1])]
            del self._data[int(params[1])]
            if len(self._roots) == 0:
                self.add_tab()

    @event('dialog/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgNew':
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
            self._new = None
