from genesis.api import *
from genesis.ui import *
from genesis import apis
from genesis.plugmgr import ImSorryDave, PluginLoader, RepositoryManager

import json
import urllib2


class PluginManager(CategoryPlugin, URLHandler):
    text = 'App Store'
    iconfont = 'gen-box-add'
    folder = 'bottom'

    def on_session_start(self):
        self._mgr = RepositoryManager(self.app.log, self.app.config)
        self._nc = apis.networkcontrol(self.app)
        self._info = None

    def on_init(self):
        self._mgr.refresh()

    def get_counter(self):
        return len(self._mgr.upgradable) or None

    def get_ui(self):
        ui = self.app.inflate('plugins:main')

        inst = sorted(self._mgr.installed, key=lambda x: x.name.lower())

        for k in inst:
            row = self.app.inflate('plugins:item')
            desc = '<span class="ui-el-label-1" style="padding-left: 5px;">%s</span>'%k.desc
            row.find('name').set('text', k.name)
            row.find('desc').set('text', k.desc)
            row.find('icon').set('class', k.iconfont)
            row.find('version').set('text', k.version)
            row.find('author').set('text', k.author)
            row.find('author').set('url', k.homepage)
            row.append('buttons', UI.TipIcon(
                        iconfont="gen-cancel-circle",
                        text='Uninstall',
                        id='remove/'+k.id,
                        warning='Are you sure you wish to remove "%s"? Software and data associated with this application will be removed.' % k.name,
                    ))

            if k.problem:
                row.find('status').set('iconfont', 'gen-close-2 text-error')
                row.find('status').set('text', k.problem)
                row.find('icon').set('class', k.iconfont + ' text-error')
                row.find('name').set('class', 'text-error')
                row.find('desc').set('class', 'text-error')
                row.append('reqs', UI.IconFont(iconfont="gen-warning text-error", text=k.problem))
            else:
                row.find('status').set('iconfont', 'gen-checkmark')
                row.find('status').set('text', 'Installed and Enabled')
            ui.append('list', row)


        lst = sorted(self._mgr.available, key=lambda x: x.name.lower())

        firstupg = False
        newapps = {}
        for k in lst:
            for p in inst:
                if k.id == p.id and not p.problem:
                    if not firstupg:
                        ui.append('upg', 
                            UI.Label(
                                size=3,
                                text="Updates Available"
                                )
                            )
                    ui.append('upg', 
                        UI.AppButton(
                            id=k.id,
                            name=k.name,
                            iconfont=k.icon,
                            version=k.version
                            )
                        )
                    firstupg = True
                    break
            else:
                for x in k.categories:
                    if not newapps.has_key(x['primary']):
                        newapps[x['primary']] = []
                    newapps[x['primary']].append(k)
        for x in newapps:
            ui.append('avail', 
                UI.Label(
                    size=3,
                    text=x
                    )
                )
            for y in newapps[x]:
                ui.append('avail', 
                    UI.AppButton(
                        id=y.id,
                        name=y.name,
                        iconfont=y.icon,
                        version=y.version
                        )
                    )

        if self._info:
            info = [x for x in self._mgr.available if x.id==self._info][0]
            if info.assets:
                try:
                    req = urllib2.Request('https://'+self.app.gconfig.get('genesis', 'update_server'))
                    req.add_header('Content-type', 'application/json')
                    resp = urllib2.urlopen(req, json.dumps({'get': 'assets', 'id': info.id}))
                    resp = json.loads(resp.read())
                    ui.find('app-logo').append(UI.Image(file="data:image/png;base64,%s" % resp['logo'], cls='app-logo'))
                    for x in resp['screenshots']:
                        ui.find('app-screens').append(UI.Image(file="data:image/jpeg;base64,%s" % x, cls="img-responsive img-thumbnail app-screenshot", lightbox=self._info))
                except:
                    pass
            ui.find('app-short').set('text', info.description)
            ui.find('app-version').set('text', info.version)
            ui.find('app-cats').set('text', '<br/>'.join(['%s: %s'%(x['primary'], ', '.join(x['secondary'])) for x in info.categories]))
            ui.find('app-name').set('text', info.name)
            ui.find('app-desc').set('text', info.long_description)
            if info.app_author:
                ui.find('app-plugauthor').set('text', info.app_author)
                ui.find('app-plughomepage').set('text', info.app_homepage)
                ui.find('app-plughomepage').set('url', info.app_homepage)
            else:
                ui.remove('app-plugauth')
            ui.find('app-author').set('text', info.author)
            ui.find('app-homepage').set('text', info.homepage)
            ui.find('app-homepage').set('url', info.homepage)
        else:
            ui.remove('dlgInfo')

        return ui

    def get_ui_upload(self):
        return UI.Uploader(
            url='/upload_plugin',
            text='Install'
        )

    @url('^/upload_plugin$')
    def upload(self, req, sr):
        vars = get_environment_vars(req)
        f = vars.getvalue('file', None)
        try:
            self._mgr.install_stream(f)
        except:
            pass
        sr('301 Moved Permanently', [('Location', '/')])
        return ''

    @event('button/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'update':
            try:
                self._mgr.update_list(crit=True)
            except Exception, e:
                self.put_message('err', str(e))
                self.app.log.error(str(e))
            else:
                self.put_message('success', 'Plugin list updated')
        elif params[0] == 'remove':
            try:
                self._mgr.check_conflict(params[1], 'remove')
                lr = LiveRemove(self._mgr, params[1], self)
                lr.start()
                self._nc.remove(params[1])
            except ImSorryDave, e:
                self.put_message('err', str(e))
        elif params[0] == 'info':
            self._info = params[1]

    @event('dialog/submit')
    def on_submit(self, event, params, vars = None):
        if params[0] == 'dlgInfo':
            if vars.getvalue('action', '') == 'OK':
                try:
                    self._mgr.check_conflict(self._info, 'install')
                    self._mgr.install(self._info, True, self)
                    ComponentManager.get().rescan()
                    ConfManager.get().rescan()
                    self._nc.refresh()
                except Exception, e:
                    self.put_message('err', str(e))
                finally:
                    self.put_message('success', 'Plugin installed successfully!')
            self._info = None
