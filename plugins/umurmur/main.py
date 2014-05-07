from genesis.ui import *
from genesis.api import *
from genesis import apis
import backend


class UMurmurPlugin(apis.services.ServiceControlPlugin):
    text = 'Mumble Server'
    iconfont = 'gen-phone'
    folder = 'servers'

    def on_session_start(self):
        self._config = backend.UMurmurConfig(self.app)
        self._config.load()
        self._tab = 0
        self._open_dialog = None
        self.update_services()

    def get_main_ui(self):
        ui = self.app.inflate('umurmur:main')
        ui.find('tabs').set('active', 'tab' + str(self._tab))
        cfg = self._config.config

        if not hasattr(cfg, "channels"):
            ui.remove('dlg_add_chan')
            ui.remove('dlg_add_chan_lnk')
            ui.append("container_settings", UI.Label(
                text="uMurmur settings file damaged. "
                     "Please reinstall uMurmur",
                size=3)
            )
            return ui

        # Tab 0: General Server Settings
        content = UI.FormBox(
            UI.FormLine(
                UI.TextInput(
                    name="welcometext",
                    value=cfg.get("welcometext", ""),
                ),
                text="Welcome text"
            ),
            UI.FormLine(
                UI.TextInput(
                    name="password",
                    value=cfg.get("password", ""),
                    password=True
                ),
                text="Server password"
            ),
            UI.FormLine(
                UI.TextInput(
                    name="max_bandwidth",
                    value=cfg.get("max_bandwidth", 48000),
                ),
                text="Max. bandwidth",
                help="In bits/second/user",
            ),
            UI.FormLine(
                UI.TextInput(
                    name="max_users",
                    value=cfg.get("max_users", 10),
                ),
                text="Max. users"
            ),
            id="form_server"
        )
        ui.append("container_settings", content)

        # Tab 1: Channels
        # TODO password for channels
        # TODO Tree View of channels
        chan_to_par = {}
        for chan in cfg.channels:
            if chan.parent:
                chan_to_par[chan.name] = chan.parent
            row = UI.DTR(
                UI.Label(text=chan.name),
                UI.Label(text=chan.parent),
                UI.Label(text=chan.description),
                UI.Label(text=("Yes" if chan.get("silent") else "No"))
            )
            ui.append('table_channels', row)

        for lnk in cfg.channel_links:
            row = UI.DTR(
                UI.Label(text=lnk.source),
                UI.Label(text="=>"),
                UI.Label(text=lnk.destination),
            )
            ui.append('table_channel_links', row)

        def_chan = cfg.default_channel
        content = UI.FormBox(
            UI.FormLine(
                UI.SelectInput(*list(
                    UI.SelectOption(text=c, value=c, selected=(c == def_chan))
                    for c in sorted(chan_to_par.keys())
                ), name="default_channel"),
                text="Default channel",
            ),
            id="form_def_chan"
        )
        ui.append("container_default_channel", content)

        non_del_channels = set(chan_to_par.values() + [def_chan])
        del_channels = list( 
            c for c in chan_to_par.keys()
            if c not in non_del_channels
        )
        content = UI.FormBox(
            UI.FormLine(
                UI.SelectInput(*list(
                    UI.SelectOption(text=c, value=c, selected=c == "(None)")
                    for c in (["(None)"] + sorted(del_channels))
                ), name="delete_channel"),
                text="Delete channel",
                help="(Only non-default channels without children)"
            ),
            id="form_del_chan"
        )
        ui.append("container_delete_channel", content)

        chan_lnks = ["(None)"] + list(
            "%s => %s" % (l.source, l.destination) for l in cfg.channel_links
        )
        content = UI.FormBox(
            UI.FormLine(
                UI.SelectInput(*list(
                    UI.SelectOption(text=c, value=c, selected=c == "(None)")
                    for c in chan_lnks
                ), name="delete_channel_link"),
                text="Delete channel link"
            ),
            id="form_del_chan_lnk"
        )
        ui.append("container_delete_channel_link", content)

        # Tab 2: Info
        # TODO: remove info tab
        for k, v in sorted(cfg.items()):
            if k in ("password", "channel_links", "channels"):
                continue
            e = UI.DTR(
                UI.IconFont(iconfont='gen-folder'),
                UI.Label(text=k),
                UI.Label(text=v),
            )
            ui.append('all_config', e)

        # dialogs
        if self._open_dialog == 'add_channel':
            content = UI.SimpleForm(
                UI.FormLine(
                    UI.TextInput(
                        name="chan_name",
                        value=""
                    ),
                    text="Channel name"
                ),
                UI.FormLine(
                    UI.TextInput(
                        name="chan_descr",
                        value=""
                    ),
                    text="Channel description"
                ),
                UI.FormLine(
                    UI.SelectInput(*list(
                        UI.SelectOption(text=c, value=c)
                        for c in (["Root"] + sorted(chan_to_par.keys())),
                    ), name="chan_parent"),
                    text="Parent channel"
                ),
                UI.FormLine(
                    UI.CheckBox(
                        name="chan_silent",
                        text="Yes",
                        checked=False,
                    ),
                    text="Silent",
                    #TODO: help="" (checkout silent mode before... )
                ),
                id="dialog_add_channel"
            )
            ui.append("container_add_channel", content)
        else:
            ui.remove('dlg_add_chan')

        if self._open_dialog == 'add_channel_link':
            content = UI.SimpleForm(
                UI.FormLine(
                    UI.SelectInput(*list(
                        UI.SelectOption(text=c, value=c)
                        for c in sorted(chan_to_par.keys()),
                    ), name="chan_src"),
                    text="Source channel"
                ),
                UI.FormLine(
                    UI.SelectInput(*list(
                        UI.SelectOption(text=c, value=c)
                        for c in sorted(chan_to_par.keys()),
                    ), name="chan_dest"),
                    text="Destination channel"
                ),
                id="dialog_add_channel_link"
            )
            ui.append("container_add_channel_link", content)
        else:
            ui.remove('dlg_add_chan_lnk')

        self._open_dialog = None
        return ui

    @event('button/click')
    def on_click(self, event, params, vars=None):
        self._open_dialog = params[0]


    @event('form/submit')
    def on_submit(self, event, params, vars=None):
        cfg = self._config.config

        # server settings
        if params[0] == 'form_server':
            self._tab = 0
            if vars.getvalue('action', '') == 'OK':
                cfg.set(
                    "welcometext",
                    vars.getvalue("welcometext", "")
                )
                cfg.set(
                    "password",
                    vars.getvalue("password", "")
                )
                try:
                    cfg.set(
                        "max_bandwidth",
                        int(vars.getvalue("max_bandwidth", ""))
                    )
                except ValueError:
                    self.put_message(
                        'warn', '"Max. bandwidth" must be an integer value.'
                    )
                try:
                    cfg.set(
                        "max_users",
                        int(vars.getvalue("max_users", ""))
                    )
                except ValueError:
                    self.put_message(
                        'warn', '"Max. users" must be an integer value.'
                    )
                self._config.save()

        # channel settings
        if params[0] == 'form_def_chan':
            self._tab = 1
            if vars.getvalue('action', '') == 'OK':
                cfg.set("default_channel", vars.getvalue("default_channel"))
                self._config.save()

        if params[0] == 'form_del_chan':
            self._tab = 1
            del_chan = vars.getvalue("delete_channel")
            for chan in cfg.channels[:]:
                if del_chan == chan.name:
                    cfg.channels.remove(chan)
                    break
            for lnk in cfg.channel_links[:]:
                if del_chan in (lnk.source, lnk.destination):
                    cfg.channel_links.remove(lnk)
            self._config.save()

        if params[0] == 'form_del_chan_lnk':
            self._tab = 1
            src, dest = vars.getvalue("delete_channel_link").split(" => ")
            for lnk in cfg.channel_links[:]:
                if src == lnk.source and dest == lnk.destination:
                    cfg.channel_links.remove(lnk)
            self._config.save()

        if vars.getvalue('action', '') == 'Cancel':
            self._config.load()

    @event('dialog/submit')
    def on_submit_dlg(self, event, params, vars=None):
        if vars.getvalue('action', '') != 'OK':
            return

        cfg = self._config.config
        if params[0] == 'dlg_add_chan':

            chan_name = vars.getvalue('chan_name')
            if not chan_name:
                self.put_message('warn', 'Channel name cannot be empty.')
                return

            if chan_name.lower() in (n.name.lower() for n in cfg.channels):
                self.put_message('warn', 'Channel name already exists.')
                return

            new_chan = backend.pylibconfig2.ConfGroup()
            setattr(new_chan, "name", chan_name)
            setattr(new_chan, "description", vars.getvalue('chan_descr'))
            setattr(new_chan, "parent", vars.getvalue('chan_parent'))
            if vars.getvalue('chan_silent'):
                setattr(new_chan, "silent", True),
            cfg.channels.append(new_chan)
            self._config.save()
            self._tab = 1

        if params[0] == 'dlg_add_chan_lnk':
            chan_src = vars.getvalue('chan_src')
            chan_dest = vars.getvalue('chan_dest')
            if chan_src == chan_dest:
                self.put_message(
                    'warn', "Nope. I won't make a link with src == dest."
                )
                return
            new_lnk = backend.pylibconfig2.ConfGroup()
            setattr(new_lnk, "source", chan_src)
            setattr(new_lnk, "destination", chan_dest)
            cfg.channel_links.append(new_lnk)
            self._config.save()
            self._tab = 1

# TODO: check input for all submits
# TODO: Warning message if no cert assigned
# TODO: Move website content from here to layout file