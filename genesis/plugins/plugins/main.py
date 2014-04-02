from genesis.api import *
from genesis.ui import *
from genesis import apis
from genesis.plugmgr import ImSorryDave, PluginLoader, RepositoryManager, LiveInstall, LiveRemove


class PluginManager(CategoryPlugin, URLHandler):
    text = 'Applications'
    iconfont = 'gen-box-add'
    folder = None

    def on_session_start(self):
        self._mgr = RepositoryManager(self.app.log, self.app.config)
        self._nc = apis.networkcontrol(self.app)
        self._reloadfw = False

    def on_init(self):
        self._mgr.refresh()

    def get_counter(self):
        return len(self._mgr.upgradable) or None

    def get_ui(self):
        if self._reloadfw == True:
            self._nc.refresh()
            self._reloadfw = False

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

        btn = UI.Button(text='Check for updates', id='update')
        if len(lst) == 0:
            btn['text'] = 'Download plugin list'

        for k in lst:
            row = self.app.inflate('plugins:item')
            row.find('name').set('text', k.name)
            row.find('desc').set('text', k.description)
            row.find('icon').set('class', k.icon)
            row.find('version').set('text', k.version)
            row.find('author').set('text', k.author)
            row.find('author').set('url', k.homepage)

            for p in inst:
                if k.id == p.id and not p.problem:
                    row.find('status').set('iconfont', 'gen-arrow-up-2')
                    row.find('status').set('text', 'Upgrade Available')

            reqs = k.str_req()

            url = 'http://%s/view/plugins.php?id=%s' % (
                    self.app.config.get('genesis', 'update_server'),
                    k.id
                   )

            if reqs == '':
                row.append('buttons', UI.TipIcon(
                        iconfont="gen-box-add",
                        text='Download and install',
                        id='install/'+k.id,
                    ))
            else:
                row.append('reqs', UI.Icon(iconfont="gen-warning", text=reqs))

            ui.append('avail', row)

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
                self.put_message('info', 'Plugin list updated')
        if params[0] == 'remove':
            try:
                self._mgr.check_conflict(params[1], 'remove')
                lr = LiveRemove(self._mgr, params[1], self)
                lr.start()
                self._nc.remove(params[1])
            except ImSorryDave, e:
                self.put_message('err', str(e))
        if params[0] == 'reload':
            try:
                PluginLoader.unload(params[1])
            except:
                pass
            try:
                PluginLoader.load(params[1])
            except:
                pass
            self.put_message('info', 'Plugin reloaded. Refresh page for changes to take effect.')
        if params[0] == 'restart':
            self.app.restart()
        if params[0] == 'install':
            try:
                self._mgr.check_conflict(params[1], 'install')
                li = LiveInstall(self._mgr, params[1], 
                    True, self)
                li.start()
            except Exception, e:
                self.put_message('err', str(e))
