import gevent
import platform
import json

from genesis.ui import UI
from genesis.com import *
from genesis import version
from genesis.api import ICategoryProvider, EventProcessor, SessionPlugin, event, URLHandler, url, get_environment_vars
from genesis.ui import BasicTemplate
from genesis.utils import send_json, ConfigurationError, shell
from api import IProgressBoxProvider


class RootDispatcher(URLHandler, SessionPlugin, EventProcessor, Plugin):
    # Plugin folders. This dict is here forever^W until we make MUI support
    folders = {
        'cluster': 'CLUSTER',
        'system': 'SYSTEM',
        'hardware': 'HARDWARE',
        'apps': 'APPLICATIONS',
        'servers': 'SERVERS',
        'advanced': 'ADVANCED',
        'other': 'OTHER',
    }

    # Folder order
    folder_ids = ['cluster', 'apps', 'servers', 'system', 'hardware', 'advanced', 'other']

    def on_session_start(self):
        self._cat_selected = 'firstrun' if self.is_firstrun() else 'homeplugin'
        self._help_visible = False
        self._about_visible = False
        self._module_config = None

    def is_firstrun(self):
        return not self.app.gconfig.has_option('genesis', 'firstrun')

    def main_ui(self):
        self.selected_category.on_init()
        templ = self.app.inflate('core:main')

        if self.app.config.get('genesis', 'nofx', '') != '1':
            templ.remove('fx-disable')

        ta = self.app.config.get('genesis', 'timedalert', '')
        templ.find('timed-alerts').append(UI.JS(code='var timedAlerts = %s;'%ta if ta else '0'))

        if self._about_visible:
            templ.append('main-content', self.get_ui_about())

        if self._help_visible:
            templ.append('main-content', self.get_ui_help())

        templ.append('main-content', self.selected_category.get_ui())

        if self.is_firstrun() and self.app.session.has_key('messages'):
            del self.app.session['messages']
        if self.app.session.has_key('messages'):
            for msg in self.app.session['messages']:
                if 'info' in msg[0]:
                    msgcls, ift = 'info', 'gen-info'
                elif 'warn' in msg[0]:
                    msgcls, ift = 'warning', 'gen-warning'
                elif 'success' in msg[0]:
                    msgcls, ift = 'success', 'gen-checkmark'
                else:
                    msgcls, ift = 'danger', 'gen-close'
                templ.append(
                    'message-box',
                    UI.SystemMessage(
                        cls=msgcls,
                        iconfont=ift,
                        text=msg[1],
                    )
                )
            del self.app.session['messages']
        return templ

    def do_init(self):
        # end firstrun wizard
        if self._cat_selected == 'firstrun' and not self.is_firstrun():
            self._cat_selected = 'dashboard'

        cat = None
        for c in self.app.grab_plugins(ICategoryProvider):
            if c.plugin_id == self._cat_selected: # initialize current plugin
                cat = c
        self.selected_category = cat

    def get_ui_about(self):
        ui = self.app.inflate('core:about')
        ui.find('ver').set('text', version())
        return ui

    def get_ui_help(self):
        ui = self.app.inflate('core:help')
        ui.find('dlgHelp').set('title', 'Help: %s' % self.selected_category.text)
        try:
            ui.find('help-container').append(self.app.inflate('%s:help'%self.selected_category.pid))
        except:
            ui.find('help-container').append(UI.Label(size=1, text='No help found for this plugin'))
        return ui

    @url('^/error$')
    def handle_errorrpt(self, req, sr):
        url = self.app.config.get('genesis', 'update_server', 'grm.arkos.io')
        try:
            rpt = json.loads(req['wsgi.input'].read())
            data = send_json('https://%s/' % url, 
                {'put': 'crashreport', 'report': rpt['report'], 'comments': rpt['comments']}, crit=True)
            if data['status'] == 200:
                self.app.log.info('An automatic error report was filed to %s' % url)
                return json.dumps({"status": 200})
            else:
                self.app.log.error('Automatic error report filing failed: An unspecified server error occurred, please contact arkOS maintainers')
                return json.dumps({"status": 500})
        except Exception, e:
            self.app.log.error('Automatic error report filing failed: %s' % str(e))
            return json.dumps({"status": 500})

    @url('^/core/progress$')
    def serve_progress(self, req, sr):
        r = []
        rm = []
        if self.app.session.has_key('statusmsg'):
            # Look for new messages pushed to the queue
            for msg in self.app.session['statusmsg']:
                if msg[1]:
                    r.append({
                        'id': msg[0],
                        'type': 'statusbox',
                        'owner': msg[0],
                        'status': msg[1]
                    })
                    clear = False
                    rm.append(msg)
            # Remove messages from queue when they are shown
            self.app.session['statusmsg'] = []
        for p in sorted(self.app.grab_plugins(IProgressBoxProvider)):
            if p.has_progress():
                r.append({
                    'id': p.plugin_id,
                    'type': 'progressbox',
                    'owner': p.title,
                    'status': p.get_progress(),
                    'can_abort': p.can_abort
                })
        return json.dumps(r)
    
    @url('^/$')
    def process(self, req, start_response):
        self.do_init()

        if self.is_firstrun():
            templ = self.app.get_template('firstrun.xml')
        else:
            templ = self.app.get_template('index.xml')
            if self.app.platform == 'arkos':
                templ.remove('navbar-brand')
                templ.append('navbar-brand-div', UI.Image(cls='navbar-brand', file='/dl/core/ui/arkos.png'))

        # Sort plugins into menus where necessary
        cats = self.app.grab_plugins(ICategoryProvider)
        cats = sorted(cats, key=lambda p: p.text)

        if not self.is_firstrun():
            for c in cats:
                if c.folder in ['top', 'bottom']:
                    templ.append(
                        'topplaceholder-'+c.folder,
                        UI.TopCategory(
                            text=c.text,
                            id=c.plugin_id,
                            iconfont=c.iconfont,
                            counter=c.get_counter(),
                            selected=c==self.selected_category
                        )
                    )
                elif c.folder == 'tools':
                    templ.append(
                        'tools-placeholder',
                        UI.PopoverLink(iconfont=c.iconfont, text=c.text,
                            onclick="Genesis.selectCategory('"+c.plugin_id+"');", 
                        )
                    )
            templ.append('_head', UI.HeadTitle(text='Genesis @ %s'%platform.node()))
            templ.append('version', UI.Label(text='Genesis '+version(), size=2))
            templ.insertText('cat-username', self.app.auth.user)
            templ.appendAll('links', 
                    UI.LinkLabel(iconfont='gen-info', text='About', id='about'),
                )

        return templ.render()

    @url('^/session_reset$')
    def process_reset(self, req, start_response):
        self.app.session.clear()
        start_response('302 Found', [('Location', '/')])
        return ''

    @url('^/logout$')
    def process_logout(self, req, start_response):
        self.app.auth.deauth()
        start_response('302 Found', [('Location', '/')])
        return ''

    @url('^/redir/.+')
    def goto_embed(self, req, start_response):
        path = req['PATH_INFO'].split('/')
        host = req['HTTP_HOST']
        bhost = req['HTTP_HOST'].split(':')[0]
        ssl = False

        if len(path) >= 4 and path[3] == 'ssl':
            ssl = True

        start_response('301 Moved Permanently', [('Location', 
            ('https://' if ssl else 'http://')+bhost+':'+path[2])])
        return ''

    @event('category/click')
    def handle_category(self, event, params, **kw):
        if not isinstance(params, list):
            return
        if len(params) != 1:
            return

        self._cat_selected = 'firstrun' if self.is_firstrun() else params[0]
        self.do_init()

    @event('linklabel/click')
    def handle_linklabel(self, event, params, vars=None):
        if params[0] == 'about':
            self._about_visible = True

    @event('button/click')
    def handle_btns(self, event, params, vars=None):
        if params[0] == 'aborttask':
            for p in self.app.grab_plugins(IProgressBoxProvider):
                if p.plugin_id == params[1] and p.has_progress():
                    p.abort()
        elif params[0] == 'help':
            self._help_visible = True
        if params[0] == 'gen_reload':
            self.app.restart()
        if params[0] == 'gen_shutdown':
            shell('shutdown -P now')
        if params[0] == 'gen_reboot':
            shell('reboot')

    @event('dialog/submit')
    def handle_dlg(self, event, params, vars=None):
        if params[0] == 'dlgAbout':
            self._about_visible = False
        if params[0] == 'dlgHelp':
            self._help_visible = False

    @url('^/handle/.+')
    def handle_generic(self, req, start_response):
        # Iterate through the IEventDispatchers and find someone who will take care of the event
        # TODO: use regexp for shorter event names, ex. 'btn_clickme/click'
        path = req['PATH_INFO'].split('/')
        event = '/'.join(path[2:4])
        params = path[4:]


        try:
            self.do_init()
            self.selected_category.on_init()
        except ConfigurationError, e:
            # ignore problems if we are leaving the plugin anyway
            if params[0] == self._cat_selected or event != 'category/click':
                raise

        # Current module
        cat = self.app.grab_plugins(ICategoryProvider, lambda x: x.plugin_id == self._cat_selected)[0]

        # Search self and current category for event handler
        vars = get_environment_vars(req)
        for handler in (cat, self):
            if handler.match_event(event):
                result = handler.event(event, params, vars = vars)
                if isinstance(result, str):
                    # For AJAX calls that do not require information
                    # just return ''
                    return result
                if isinstance(result, BasicTemplate):
                    # Useful for inplace AJAX calls (that returns partial page)
                    return result.render()

        # We have no result or handler - return default page
        main = self.main_ui()
        return main.render()
