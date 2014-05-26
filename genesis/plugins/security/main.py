from genesis.ui import *
from genesis.com import implements
from genesis.api import *
from genesis import apis
from genesis.utils import *
from genesis.plugins.network.api import *

from firewall import RuleManager, FWMonitor
from defense import F2BManager, F2BConfigNotFound
from backend import *


class SecurityPlugin(apis.services.ServiceControlPlugin):
    text = 'Security'
    iconfont = 'gen-lock-2'
    folder = None
    services = [{"name": 'Intrusion Prevention', "binary": 'fail2ban', "ports": []}]
    f2b_name = 'Genesis'
    f2b_icon = 'gen-arkos-round'
    f2b = [{
        'custom': True,
        'name': 'genesis',
        'jail_opts': [
            ('enabled', 'true'),
            ('filter', 'genesis'),
            ('logpath', '/var/log/genesis.log'),
            ('action', 'iptables[name=genesis, port=8000, protocol=tcp]')
        ],
        'filter_name': 'genesis',
        'filter_opts': [
            ('_daemon', 'genesis-panel'),
            ('failregex', '.*[ERROR] auth: Login failed for user .* from <HOST>$')
        ]
    }]

    defactions = ['ACCEPT', 'DROP', 'REJECT', 'LOG', 'EXIT', 'MASQUERADE']

    def on_init(self):
        self.cfg = Config(self.app)
        self.cfg.load()
        self.net_config = self.app.get_backend(INetworkConfig)
        self.rules = sorted(self._srvmgr.get_all(), 
            key=lambda s: s[0].name)
        try:
            self.f2brules = sorted(self._f2bmgr.get_all(),
                key= lambda s: s['name'])
        except F2BConfigNotFound, e:
            self.put_message('err', e)
            self.f2brules = []

    def on_session_start(self):
        self._idef = None
        self._stab = 0
        self._tab = 0
        self._shuffling = None
        self._shuffling_table = None
        self._adding_chain = None
        self._editing_table = None
        self._editing_chain = None
        self._editing_rule = None
        self._error = None
        self._ranges = []
        self._srvmgr = RuleManager(self.app)
        self._fwmgr = FWMonitor(self.app)
        self._f2bmgr = F2BManager(self.app)

    def get_main_ui(self):
        ui = self.app.inflate('security:main')
        ui.find('stabs').set('active', 's'+str(self._stab))
        if self.cfg.has_autostart():
            btn = ui.find('autostart')
            btn.set('text', 'Disable autostart')
            btn.set('id', 'noautostart')

        present = False
        try:
            if self.app.gconfig.get('security', 'noinit') == 'yes':
                present = True
        except:
            pass
        for rx in iptc.Chain(iptc.Table(iptc.Table.FILTER), 'INPUT').rules:
            if rx.target.name == 'genesis-apps':
                present = True
            elif rx.target.name == 'DROP':
                present = True
        if present == False:
            self.put_message('err', 'There may be a problem with your '
                'firewall. Please reload the table by clicking "Reinitialize" '
                'under the Settings tab below.')

        self._ranges = []
        for x in self.net_config.interfaces:
            i = self.net_config.interfaces[x]
            r = self.net_config.get_ip(i.name)
            if '127.0.0.1' in r or '0.0.0.0' in r:
                continue
            if not '/' in r:
                ri = r
                rr = '32'
            else:
                ri, rr = r.split('/')
            ri = ri.split('.')
            ri[3] = '0'
            ri = ".".join(ri)
            r = ri + '/' + rr
            self._ranges.append(r)
        ui.find('ranges').set('text', 'Local networks: ' + ', '.join(self._ranges))

        al = ui.find('applist')
        ql = ui.find('arkoslist')
        fl = ui.find('f2blist')

        for s in self.rules:
            if s[0].plugin_id != 'arkos':
                if s[1] == 1:
                    perm, ic, show = 'Local Only', 'gen-home', [2, 0]
                elif s[1] == 2:
                    perm, ic, show = 'All Networks', 'gen-earth', [1, 0]
                else:
                    perm, ic, show = 'None', 'gen-close', [2, 1]
                al.append(UI.DTR(
                    UI.IconFont(iconfont=s[0].icon),
                    UI.Label(text=s[0].name),
                    UI.Label(text=', '.join(str(x[1]) for x in s[0].ports)),
                    UI.HContainer(
                        UI.IconFont(iconfont=ic),
                        UI.Label(text=' '),
                        UI.Label(text=perm),
                        ),
                    UI.HContainer(
                        (UI.TipIcon(iconfont='gen-earth',
                            text='Allow From Anywhere', id='2/' + str(self.rules.index(s))) if 2 in show else None),
                        (UI.TipIcon(iconfont='gen-home',
                            text='Local Access Only', id='1/' + str(self.rules.index(s))) if 1 in show else None),
                        (UI.TipIcon(iconfont='gen-close', 
                            text='Deny All', 
                            id='0/' + str(self.rules.index(s)), 
                            warning='Are you sure you wish to deny all access to %s? '
                            'This will prevent anyone (including you) from connecting to it.' 
                            % s[0].name) if 0 in show else None),
                        ),
                   ))
            else:
                if s[0].server_id == 'beacon' and s[1] == 2:
                    self._srvmgr.set(s[0], 1)
                    perm, ic, show = 'Local Only', 'gen-home', [0]
                elif s[0].server_id == 'beacon' and s[1] == 1:
                    perm, ic, show = 'Local Only', 'gen-home', [0]
                elif s[0].server_id == 'beacon' and s[1] == 0:
                    perm, ic, show = 'None', 'gen-close', [1]
                elif s[0].server_id == 'genesis' and s[1] == 2:
                    perm, ic, show = 'All Networks', 'gen-earth', [1]
                elif s[0].server_id == 'genesis' and s[1] == 1:
                    perm, ic, show = 'Local Only', 'gen-home', [2]
                ql.append(UI.DTR(
                    UI.IconFont(iconfont=s[0].icon),
                    UI.Label(text=s[0].name),
                    UI.Label(text=', '.join(str(x[1]) for x in s[0].ports)),
                    UI.HContainer(
                        UI.IconFont(iconfont=ic),
                        UI.Label(text=' '),
                        UI.Label(text=perm),
                        ),
                    UI.HContainer(
                        (UI.TipIcon(iconfont='gen-earth',
                            text='Allow From Anywhere', id='2/' + str(self.rules.index(s))) if 2 in show else None),
                        (UI.TipIcon(iconfont='gen-home',
                            text='Local Access Only', id='1/' + str(self.rules.index(s))) if 1 in show else None),
                        (UI.TipIcon(iconfont='gen-close', 
                            text='Deny All', 
                            id='0/' + str(self.rules.index(s)), 
                            warning='Are you sure you wish to deny all access to %s? '
                            'This will prevent anyone (including you) from connecting to it.' 
                            % s[0].name) if 0 in show else None),
                        ),
                   ))

        for s in self.f2brules:
            perm, ic, show = 'Disabled', 'gen-close', 'e'
            for f in s['f2b']:
                for line in f['jail_opts']:
                    if line[0] == 'enabled' and line[1] == 'true':
                        perm, ic, show = 'Enabled', 'gen-checkmark-circle', 'd'
            fl.append(UI.DTR(
                UI.IconFont(iconfont=s['icon']),
                UI.Label(text=s['name']),
                UI.HContainer(
                    UI.IconFont(iconfont=ic),
                    UI.Label(text=' '),
                    UI.Label(text=perm),
                    ),
                UI.HContainer(
                    UI.TipIcon(iconfont='gen-info', text='Information',
                        id='idef/' + str(self.f2brules.index(s))),
                    (UI.TipIcon(iconfont='gen-checkmark-circle',
                        text='Enable All Defense', id='edef/' + str(self.f2brules.index(s))) if show == 'e' else None),
                    (UI.TipIcon(iconfont='gen-close',
                        text='Disable All Defense', id='ddef/' + str(self.f2brules.index(s))) if show == 'd' else None),
                    ),
               ))

        tc = UI.TabControl(active=self._tab)
        ui.append('advroot', tc)

        if len(self.cfg.tables) == 0:
            self.cfg.load_runtime()

        for t in self.cfg.tables:
            t = self.cfg.tables[t]
            vc = UI.VContainer(spacing=15)
            for ch in t.chains:
                ch = t.chains[ch]
                uic = UI.FWChain(tname=t.name, name=ch.name, default=ch.default)
                idx = 0
                for r in ch.rules:
                    uic.append(
                        UI.FWRule(
                            action=r.action,
                            desc=('' if r.action in self.defactions else r.action + ' ') + r.desc,
                            id='%s/%s/%i'%(t.name,ch.name,idx)
                        ))
                    idx += 1
                vc.append(uic)
            vc.append(UI.Btn(iconfont='gen-plus-circle', text='Add new chain to '+t.name, id='addchain/'+t.name))
            tc.add(t.name, vc)

        try:
            ui.find('f2b_maxretry').set('value', self._f2bmgr.maxretry())
            ui.find('f2b_findtime').set('value', self._f2bmgr.findtime())
            ui.find('f2b_bantime').set('value', self._f2bmgr.bantime())
        except F2BConfigNotFound:
            ui.find('f2b_maxretry').set('disabled', 'true')
            ui.find('f2b_findtime').set('disabled', 'true')
            ui.find('f2b_bantime').set('disabled', 'true')
            ui.remove('frmDefenseButton')

        if self._idef is not None:
            ui.find('f2b_appname').set('text', self._idef['name'])
            for j in self._idef['f2b']:
                perm, ic, show = 'Disabled', 'gen-close', 'e'
                for line in j['jail_opts']:
                    if line[0] == 'enabled' and line[1] == 'true':
                        perm, ic, show = 'Enabled', 'gen-checkmark-circle', 'd'
                ui.find('f2b_jails').append(
                    UI.DTR(
                        UI.Label(text=j['name']),
                        UI.HContainer(
                            (UI.TipIcon(iconfont='gen-checkmark-circle',
                                text='Enable', id='ed/' + j['name']) if show == 'e' else None),
                            (UI.TipIcon(iconfont='gen-close',
                                text='Disable', id='dd/' + j['name']) if show == 'd' else None),
                        ),
                    ))
        else:
            ui.remove('dlgF2BInfo')

        if self._error is not None and len(self._error) > 0:
            self.put_message('warn', self._error)
            self._error = None

        if self._shuffling != None:
            ui.append('advroot', self.get_ui_shuffler())

        if self._adding_chain != None:
            ui.append('advroot', UI.InputBox(id='dlgAddChain', text='Chain name:'))

        if self._editing_rule != None:
            ui.append('advroot', self.get_ui_edit_rule(
                        rule=self.cfg.tables[self._editing_table].\
                                      chains[self._editing_chain].\
                                      rules[self._editing_rule]
                    ))

        return ui

    def get_ui_edit_rule(self, rule=Rule()):
        protocols = (('TCP','tcp'), ('UDP','udp'), ('ICMP','icmp'))

        tc = UI.TabControl(active='r0')
        tc.add('Main',
            UI.Container(
                UI.Formline(
                    UI.Radio(text='Accept', name='caction', value='ACCEPT',     checked=rule.action=="ACCEPT"),
                    UI.Radio(text='Drop',   name='caction', value='DROP',       checked=rule.action=="DROP"),
                    UI.Radio(text='Reject', name='caction', value='REJECT',     checked=rule.action=="REJECT"),
                    UI.Radio(text='Log',    name='caction', value='LOG',        checked=rule.action=="LOG"),
                    UI.Radio(text='Masq',   name='caction', value='MASQUERADE', checked=rule.action=="MASQUERADE"),
                    UI.Radio(text='Exit',   name='caction', value='EXIT',       checked=rule.action=="EXIT"),
                    UI.Radio(text='Run chain:', name='caction', value='RUN',    checked=rule.action not in self.defactions),
                    UI.TextInput(name='runchain', value=rule.action),
                    text='Action'
                ),
                UI.Formline(
                    rule.get_ui_select('protocol', protocols),
                    text='Protocol'
                ),
                UI.Formline(
                    rule.get_ui_text('source'),
                    text='Source IP',
                    help='You can specify IP mask like 192.168.0.0/24'
                ),
                UI.Formline(
                    rule.get_ui_text('destination'),
                    text='Destination IP',
                ),
                UI.Formline(
                    rule.get_ui_text('mac_source'),
                    text='Source MAC'
                ),
                UI.Formline(
                    rule.get_ui_select('in_interface', self.cfg.get_devices()),
                    text='Incoming interface'
                ),
                UI.Formline(
                    rule.get_ui_select('out_interface', self.cfg.get_devices()),
                    text='Outgoing interface'
                ),
                UI.Formline(
                    rule.get_ui_bool('fragmented'),
                    text='Fragmentation'
                ),
                UI.Formline(
                    UI.TextInput(name='modules', value=' '.join(rule.modules)),
                    text='Modules',
                    help='Additional IPTables modules to load',
                ),
                UI.Formline(
                    UI.TextInput(name='options', value=' '.join(rule.miscopts)),
                    text='Additional options',
                ),
            ), id='r0')

        tc.add('TCP/UDP',
            UI.Container(
                UI.Formline(
                    rule.get_ui_text('sport'),
                    text='Source port',
                    help='Can accept lists and ranges like 80:85,8000 up to 15 ports',
                ),
                UI.Formline(
                    rule.get_ui_text('dport'),
                    text='Destination port'
                ),
                UI.Formline(
                    rule.get_ui_flags(),
                    text='TCP flags',
                ),
                UI.Formline(
                    rule.get_ui_states(),
                    text='TCP states',
                ),
            ), id='r1')

        return UI.DialogBox(tc, id='dlgEditRule', miscbtn='Delete', miscbtnid='deleterule')

    def get_ui_shuffler(self):
        li = UI.SortList(id='list')
        for r in self.cfg.tables[self._shuffling_table].chains[self._shuffling].rules:
            li.append(
                UI.SortListItem(
                    UI.FWRule(action=r.action, desc=r.desc, id=''),
                    id=r.raw
                ))

        return UI.DialogBox(li, id='dlgShuffler')

    @event('button/click')
    def on_click(self, event, params, vars=None):
        if params[0] == '2':
            self._stab = 0
            self._srvmgr.set(self.rules[int(params[1])][0], 2)
            self._fwmgr.regen(self._ranges)
        if params[0] == '1':
            self._stab = 0
            self._srvmgr.set(self.rules[int(params[1])][0], 1)
            self._fwmgr.regen(self._ranges)
        if params[0] == '0':
            self._stab = 0
            sel = self.rules[int(params[1])][0]
            if sel.plugin_id == 'arkos' and sel.server_id == 'genesis':
                self.put_message('err', 'You cannot deny all access to Genesis. '
                    'Try limiting it to your local network instead.')
            else:
                self._srvmgr.set(sel, 0)
                self._fwmgr.regen(self._ranges)
        if params[0] == 'idef':
            self._stab = 1
            self._idef = self.f2brules[int(params[1])]
        if params[0] == 'ed':
            self._stab = 1
            try:
                self._f2bmgr.enable_jail(params[1])
            except F2BConfigNotFound, e:
                self.put_message('err', e)
        if params[0] == 'dd':
            self._stab = 1
            try:
                self._f2bmgr.disable_jail(params[1])
            except F2BConfigNotFound, e:
                self.put_message('err', e)
        if params[0] == 'edef':
            self._stab = 1
            try:
                self._f2bmgr.enable_all(self.f2brules[int(params[1])])
            except F2BConfigNotFound, e:
                self.put_message('err', e)
        if params[0] == 'ddef':
            self._stab = 1
            try:
                self._f2bmgr.disable_all(self.f2brules[int(params[1])])
            except F2BConfigNotFound, e:
                self.put_message('err', e)
        if params[0] == 'reinit':
            self._stab = 3
            self._fwmgr.initialize()
        if params[0] == 'apply':
            self._stab = 2
            self._error = self.cfg.apply_now()
        if params[0] == 'autostart':
            self._stab = 2
            self.cfg.set_autostart(True)
        if params[0] == 'noautostart':
            self._stab = 2
            self.cfg.set_autostart(False)
        if params[0] == 'loadruntime':
            self._stab = 2
            self.cfg.load_runtime()
        if params[0] == 'setdefault':
            self._stab = 2
            self._tab = self.cfg.table_index(params[1])
            self.cfg.tables[params[1]].chains[params[2]].default = params[3]
            self.cfg.save()
        if params[0] == 'shuffle':
            self._stab = 2
            self._tab = self.cfg.table_index(params[1])
            self._shuffling_table = params[1]
            self._shuffling = params[2]
        if params[0] == 'addchain':
            self._stab = 2
            self._tab = self.cfg.table_index(params[1])
            self._adding_chain = params[1]
        if params[0] == 'deletechain':
            self._stab = 2
            self._tab = self.cfg.table_index(params[1])
            self.cfg.tables[params[1]].chains.pop(params[2])
            self.cfg.save()
        if params[0] == 'addrule':
            self._stab = 2
            self._tab = self.cfg.table_index(params[1])
            self._editing_table = params[1]
            self._editing_chain = params[2]
            ch = self.cfg.tables[self._editing_table].\
                         chains[self._editing_chain]
            self._editing_rule = len(ch.rules)
            ch.rules.append(Rule('-A %s -j ACCEPT'%params[2]))
            self.cfg.save()
        if params[0] == 'deleterule':
            self._stab = 2
            self.cfg.tables[self._editing_table].\
                     chains[self._editing_chain].\
                     rules.pop(self._editing_rule)
            self._editing_chain = None
            self._editing_table = None
            self._editing_rule = None
            self.cfg.save()

    @event('fwrule/click')
    def on_fwrclick(self, event, params, vars=None):
        self._stab = 2
        self._tab = self.cfg.table_index(params[0])
        self._editing_table = params[0]
        self._editing_chain = params[1]
        self._editing_rule = int(params[2])

    @event('form/submit')
    @event('dialog/submit')
    def on_submit(self, event, params, vars):
        if params[0] == 'frmDefense':
            self._stab = 3
            if vars.getvalue('action', '') == 'OK':
                try:
                    self._f2bmgr.maxretry(vars.getvalue('f2b_maxretry', ''))
                    self._f2bmgr.findtime(vars.getvalue('f2b_findtime', ''))
                    self._f2bmgr.bantime(vars.getvalue('f2b_bantime', ''))
                except F2BConfigNotFound:
                    pass
        if params[0] == 'dlgF2BInfo':
            self._stab = 1
            self._idef = None
        if params[0] == 'dlgAddChain':
            if vars.getvalue('action', '') == 'OK':
                n = vars.getvalue('value', '')
                if n == '': return
                self.cfg.tables[self._adding_chain].chains[n] = Chain(n, '-')
                self.cfg.save()
            self._stab = 2
            self._adding_chain = None
        if params[0] == 'dlgShuffler':
            if vars.getvalue('action', '') == 'OK':
                d = vars.getvalue('list', '').split('|')
                ch = self.cfg.tables[self._shuffling_table].chains[self._shuffling]
                ch.rules = []
                for s in d:
                    ch.rules.append(Rule(s))
                self.cfg.save()
            self._stab = 2
            self._shuffling = None
            self._shuffling_table = None
        if params[0] == 'dlgEditRule':
            if vars.getvalue('action', '') == 'OK':
                self.cfg.tables[self._editing_table].\
                         chains[self._editing_chain].\
                          rules[self._editing_rule].apply_vars(vars)
                self.cfg.save()
            self._stab = 2
            self._editing_chain = None
            self._editing_table = None
            self._editing_rule = None
