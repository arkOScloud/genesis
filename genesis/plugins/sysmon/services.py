#coding: utf-8
from genesis.com import implements
from genesis.api import *
from genesis.ui import *
from genesis.utils import *
from genesis import apis

from groups import *

import psutil
import signal
import os


class ServicesPlugin(CategoryPlugin):
    text = 'Services/Tasks'
    iconfont = 'gen-atom'
    folder = 'tools'

    rev_sort = [
        'get_cpu_percent',
        'get_memory_percent',
    ]

    def on_init(self):
        self.svc_mgr = self.app.get_backend(apis.services.IServiceManager)
        self.groupmgr = ServiceGroups(self.app)
        
    def on_session_start(self):
        self._editing = None
        self._sort = ('pid', False)
        self._info = None

    def sort_key(self, x):
        z = getattr(x,self._sort[0])
        return z() if callable(z) else z

    def get_ui(self):
        ui = self.app.inflate('sysmon:services')
        ts = ui.find('list')

        lst = sorted(self.svc_mgr.list_all(), key=lambda x: x.status)
        for svc in lst:
            row = self.get_row(svc)
            ts.append(row)

        for g in sorted(self.groupmgr.groups.keys()):
            gui = self.app.inflate('sysmon:group')
            gui.find('edit').set('id', 'edit/'+g)
            gui.find('delete').set('id', 'delgrp/'+g)
            gui.find('name').set('text', g)
            show_run = False
            show_stop = False
            for s in self.groupmgr.groups[g]:
                try:
                    svc = filter(lambda x:x.name==s, lst)[0]
                    if svc.status == 'running':
                        show_stop = True
                    else:
                        show_run = True
                    gui.append('list', self.get_row(svc))
                except:
                    pass
            if show_stop:
                gui.appendAll('btns',
                    UI.TipIcon(text='Stop all', iconfont='gen-stop', id='gstop/' + g),
                    UI.TipIcon(text='Restart all', iconfont='gen-loop-2', id='grestart/' + g)
                  )
            if show_run:
                gui.append('btns',
                    UI.TipIcon(text='Start all', iconfont='gen-play-2', id='gstart/' + g)
                )
        
            ui.append('groups', gui)

        if self._editing is not None:
            has = self._editing in self.groupmgr.groups.keys()
            eui = self.app.inflate('sysmon:edit')
            eui.find('name').set('value', self._editing)
            for svc in self.svc_mgr.list_all():
                eui.append('services', UI.Checkbox(
                    name=svc.name,
                    text=svc.name,
                    checked=has and (svc.name in self.groupmgr.groups[self._editing]),
                ))
            ui.append('main', eui)

        l = psutil.get_process_list()
        l = sorted(l, key=self.sort_key)
        if self._sort[1]:
            l = reversed(l)

        for x in l:
            try:
                ui.append('tlist', UI.DTR(
                    UI.IconFont(iconfont='gen-%s'%('play-2' if x.is_running() else 'stop')),
                    UI.Label(text=str(x.pid)),
                    UI.Label(text=str(int(x.get_cpu_percent()))),
                    UI.Label(text=str(int(x.get_memory_percent()))),
                    UI.Label(text=x.username()),
                    UI.Label(text=x.name()),
                    UI.TipIcon(
                        iconfont='gen-info',
                        id='info/%i'%x.pid,
                        text='Info'
                    )
                ))
            except:
                pass

        hdr = ui.find('sort/'+self._sort[0])
        hdr.set('text', ('↑ ' if self._sort[1] else '↓ ')+ hdr['text'])

        if self._info is not None:
            try:
                p = filter(lambda x:x.pid==self._info, l)[0]
                iui = self.app.inflate('sysmon:sysmon-info')
                iui.find('name').set('text', '%i / %s'%(p.pid,p.name()))
                iui.find('cmd').set('text', ' '.join("'%s'"%x for x in p.cmdline()))
                iui.find('uid').set('text', '%s (%s)'%(p.username(),p.uids().real))
                iui.find('gid').set('text', str(p.gids().real))
                iui.find('times').set('text', ' / '.join(str(x) for x in p.get_cpu_times()))
                if p.parent():
                    iui.find('parent').set('text', p.parent().name())
                    iui.find('parentinfo').set('id', 'info/%i'%p.parent().pid)
                else:
                    iui.remove('parentRow')

                sigs = [
                    (x, getattr(signal, x))
                    for x in dir(signal)
                    if x.startswith('SIG')
                ]

                for x in sigs:
                    iui.append('sigs', UI.SelectOption(
                        text=x[0], value=x[1]
                    ))
                ui.append('main', iui)
            except:
                pass

        return ui

    def get_row(self, svc):
        ctl = UI.HContainer()
        if svc.status == 'running':
            ctl.append(UI.TipIcon(text='Stop', iconfont='gen-stop', id='stop/%s/%s'%(svc.name, svc.stype)))
            ctl.append(UI.TipIcon(text='Restart', iconfont='gen-loop-2', id='restart/%s/%s'%(svc.name, svc.stype)))
        else:
            ctl.append(UI.TipIcon(text='Start', iconfont='gen-play-2', id='start/%s/%s'%(svc.name, svc.stype)))
        if svc.enabled == 'enabled':
            ctl.append(UI.TipIcon(text='Disable', iconfont='gen-minus-circle', id='disable/%s/%s'%(svc.name, svc.stype)))
        else:
            ctl.append(UI.TipIcon(text='Enable', iconfont='gen-plus-circle', id='enable/%s/%s'%(svc.name, svc.stype)))
        if svc.stype == 'supervisor':
            ctl.append(UI.TipIcon(text='Delete', iconfont='gen-cancel-circle', id='delete/%s/%s'%(svc.name, svc.stype)))

        fn = 'gen-' + ('play-2' if svc.status == 'running' else 'stop')
        row = UI.DTR(
                UI.IconFont(iconfont=fn),
                UI.Label(text=svc.name),
                ctl
              )
        return row
                      
    @event('button/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'start':
            self.svc_mgr.start(params[1], params[2])
        elif params[0] == 'restart':
            self.svc_mgr.restart(params[1], params[2])
        elif params[0] == 'stop':
            self.svc_mgr.stop(params[1], params[2])
        elif params[0] == 'enable':
            self.svc_mgr.enable(params[1], params[2])
        elif params[0] == 'disable':
            self.svc_mgr.disable(params[1], params[2])
        elif params[0] == 'delete':
            self.svc_mgr.delete(params[1], params[2])
        elif params[0] == 'gstart':
            for s in self.groupmgr.groups[params[1]]:
                self.svc_mgr.start(s, params[2])
        elif params[0] == 'grestart':
            for s in self.groupmgr.groups[params[1]]:
                self.svc_mgr.restart(s, params[2])
        elif params[0] == 'gstop':
            for s in self.groupmgr.groups[params[1]]:
                self.svc_mgr.stop(s, params[2])
        elif params[0] == 'addGroup':
            self._editing = ''
        elif params[0] == 'delgrp':
            del self.groupmgr.groups[params[1]]
            self.groupmgr.save()
        elif params[0] == 'edit':
            self._editing = params[1]
        if params[0] == 'info':
            self._info = int(params[1])
        elif params[0] == 'suspend':
            try:
                x = filter(lambda p:p.pid==self._info, psutil.get_process_list())[0].suspend()
            except:
                pass
        elif params[0] == 'resume':
            try:
                filter(lambda p:p.pid==self._info, psutil.get_process_list())[0].resume()
            except:
                pass

    @event('linklabel/click')
    def on_sort(self, event, params, vars=None):
        if params[1] == self._sort[0]:
            self._sort = (self._sort[0], not self._sort[1])
        else:
            self._sort = (params[1], params[1] in self.rev_sort)

    @event('dialog/submit')
    @event('form/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgEdit':
            if vars.getvalue('action') == 'OK':
                svcs = []
                for svc in self.svc_mgr.list_all():
                    if vars.getvalue(svc.name) == '1':
                        svcs.append(svc.name)
                if self._editing != '':
                    del self.groupmgr.groups[self._editing]                        
                self.groupmgr.groups[vars.getvalue('name')] = sorted(svcs)
                self.groupmgr.save()
            self._editing = None
        if params[0] == 'dlgInfo':
            self._info = None
        if params[0] == 'frmKill':
            self._info = None
            try:
                x = filter(lambda p:p.pid==self._info, psutil.get_process_list())[0]
                x.kill(int(vars.getvalue('signal', None)))
                self.put_message('info', 'Killed process')
            except:
                self.put_message('err', 'Can\'t kill process')
