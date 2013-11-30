from genesis.com import implements
from genesis.api import *
from genesis.ui import *
from genesis import apis

from groups import *


class ServicesPlugin(CategoryPlugin):
    text = 'Services'
    iconfont = 'gen-atom'
    folder = 'system'

    def on_init(self):
        self.svc_mgr = self.app.get_backend(apis.services.IServiceManager)
        self.groupmgr = ServiceGroups(self.app)
        
    def on_session_start(self):
        self._editing = None

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
            gui.find('delete').set('id', 'delete/'+g)
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

        return ui

    def get_row(self, svc):
        ctl = UI.HContainer()
        if svc.status == 'running':
            ctl.append(UI.TipIcon(text='Stop', iconfont='gen-stop', id='stop/' + svc.name))
            ctl.append(UI.TipIcon(text='Restart', iconfont='gen-loop-2', id='restart/' + svc.name))
        else:
            ctl.append(UI.TipIcon(text='Start', iconfont='gen-play-2', id='start/' + svc.name))
        if svc.enabled == 'enabled':
            ctl.append(UI.TipIcon(text='Disable', iconfont='gen-minus-circle', id='disable/' + svc.name))
        else:
            ctl.append(UI.TipIcon(text='Enable', iconfont='gen-plus-circle', id='enable/' + svc.name))

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
            self.svc_mgr.start(params[1])
        if params[0] == 'restart':
            self.svc_mgr.restart(params[1])
        if params[0] == 'stop':
            self.svc_mgr.stop(params[1])
        if params[0] == 'enable':
            self.svc_mgr.enable(params[1])
        if params[0] == 'disable':
            self.svc_mgr.disable(params[1])
        if params[0] == 'gstart':
            for s in self.groupmgr.groups[params[1]]:
                self.svc_mgr.start(s)
        if params[0] == 'grestart':
            for s in self.groupmgr.groups[params[1]]:
                self.svc_mgr.restart(s)
        if params[0] == 'gstop':
            for s in self.groupmgr.groups[params[1]]:
                self.svc_mgr.stop(s)
        if params[0] == 'addGroup':
            self._editing = ''
        if params[0] == 'delete':
            del self.groupmgr.groups[params[1]]
            self.groupmgr.save()
        if params[0] == 'edit':
            self._editing = params[1]

    @event('dialog/submit')
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

