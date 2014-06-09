from genesis.api import *
from genesis.utils import *
from genesis.ui import *

import os
import sys
import signal
import json
import gzip
import StringIO
import pty
import subprocess as sp
import fcntl
import pty
from base64 import b64decode, b64encode
from PIL import Image, ImageDraw

from gevent.event import Event
import gevent

import pyte.screens, pyte.streams


TERM_W = 160
TERM_H = 40


class TerminalPlugin(CategoryPlugin, URLHandler):
    text = 'Terminal'
    iconfont = 'gen-console'
    folder = 'tools'

    def on_session_start(self):
        self._terminals = {}
        self._tid = 1
        self._terminals[0] = Terminal()
        
    def get_ui(self):
        ui = self.app.inflate('terminal:main')
        for id in self._terminals:
            ui.find('main').append(
                UI.TblBtn(
                    UI.TipIcon(
                        iconfont='gen-cancel-circle',
                        id='kill/' + str(id),
                        text='Close'
                    ),
                    id=id,
                    outlink='/terminal/%s' % id,
                    icon='gen-console',
                    name='Terminal #%s' % id
                    )
                )
        ui.find('main').append(
            UI.TblBtn(
                id='add',
                icon='gen-plus-circle',
                name='New Terminal'
                )
            )
        return ui

    @event('button/click')
    def onclick(self, event, params, vars=None):
        if params[0] == 'add':
            self._terminals[self._tid] = Terminal()
            self._tid += 1
        elif params[0] == 'kill':
            id = int(params[1])
            self._terminals[id].kill()
            del self._terminals[id]

    @url('^/terminal/.*$')
    def get(self, req, start_response):
        params = req['PATH_INFO'].split('/')[1:] + ['']
        id = int(params[1])

        if self._terminals[id].dead():
            self._terminals[id].start(self.app.get_config(self).shell)

        if params[2] in ['history', 'get']:
            if params[2] == 'history':
                data = self._terminals[id]._proc.history()
            else:
                data = self._terminals[id]._proc.read()
            sio = StringIO.StringIO()
            gz = gzip.GzipFile(fileobj=sio, mode='w')
            gz.write(json.dumps(data))
            gz.close()
            return b64encode(sio.getvalue())

        if params[2] == 'post':
            data = params[3]
            self._terminals[id].write(b64decode(data))
            return ''

        if params[2] == 'kill':
            self._terminals[id].restart()

        page = self.app.inflate('terminal:page')
        page.find('title').text = shell('echo `whoami`@`hostname`')
        page.append('main', UI.JS(
            code='termInit(\'%i\');'%id
        ))
        return page.render()


class Terminal:
    def __init__(self):
        self._proc = None

    def start(self, app):
        env = {}
        env.update(os.environ)
        env['TERM'] = 'linux'
        env['COLUMNS'] = str(TERM_W)
        env['LINES'] = str(TERM_H)
        env['LC_ALL'] = 'en_US.UTF8'
        sh = app 

        pid, master = pty.fork()
        if pid == 0:
            p = sp.Popen(
                sh,
                shell=True,
                close_fds=True,
                env=env,
            )
            p.wait()
            sys.exit(0)
        self._proc = PTYProtocol(pid, master)

    def restart(self):
        if self._proc is not None:
            self._proc.kill()
        self.start()

    def dead(self):
        return self._proc is None 

    def write(self, data):
        self._proc.write(data)

    def kill(self):
        self._proc.kill()


class PTYProtocol():
    def __init__(self, proc, stream):
        self.data = ''
        self.proc = proc
        self.master = stream

        fd = self.master
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        self.mstream = os.fdopen(self.master, 'r+')
        gevent.sleep(2)
        self.term = pyte.screens.DiffScreen(TERM_W,TERM_H)
        self.stream = pyte.streams.Stream()
        self.stream.attach(self.term)
        self.data = ''
        self.unblock()

    def unblock(self):
        fd = self.master
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    def block(self):
        fd = self.master
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl - os.O_NONBLOCK)

    def read(self):
        cond = Event()
        def reread():
            cond.set()
            cond.clear()
        for i in range(0,45):
            try:
                d = self.mstream.read()
                self.data += d
                if len(self.data) > 0:
                    u = unicode(str(self.data))
                    self.stream.feed(u)
                    self.data = ''
                break
            except IOError, e:
                pass
            except UnicodeDecodeError, e:
                print 'UNICODE'
            gevent.spawn_later(0.33, reread)
            cond.wait(timeout=0.33)
        return self.format()

    def history(self):
        return self.format(full=True)

    def format(self, full=False):
        l = {}
        self.term.dirty.add(self.term.cursor.y)
        for k in self.term.dirty:
            l[k] = self.term.buffer[k]
        self.term.dirty.clear()
        r = {
            'lines': self.term.buffer if full else l,
            'cx': self.term.cursor.x,
            'cy': self.term.cursor.y,
            'cursor': not self.term.cursor.hidden,
        }
        return r

    def write(self, data):
        self.block()
        self.mstream.write(data)
        self.mstream.flush()
        self.unblock()

    def kill(self):
        os.kill(self.proc, 9)
