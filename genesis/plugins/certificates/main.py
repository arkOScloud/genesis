from genesis.com import *
from genesis.api import *
from genesis.ui import *
from genesis import apis
from genesis.utils import *
from genesis.plugins.network.backend import IHostnameManager

from backend import CertControl

import os
import re


class CertificatesPlugin(CategoryPlugin, URLHandler):
    text = 'Certificates'
    iconfont = 'gen-certificate'
    folder = 'system'

    def on_init(self):
        self.certs = sorted(self._cc.get_certs(),
            key=lambda x: x['name'])
        self.cas = sorted(self._cc.get_cas(),
            key=lambda x: x['name'])

    def on_session_start(self):
        self._cc = CertControl(self.app)
        self._gen = None
        self._tab = 0
        self._wal = []
        self._pal = []
        self._upload = None

    def get_ui(self):
        ui = self.app.inflate('certificates:main')
        ui.find('tabs').set('active', self._tab)

        cfg = self.app.get_config(CertControl(self.app))
        ui.find('kl'+cfg.keylength).set('selected', True)
        ui.find('kt'+cfg.keytype.lower()).set('selected', True)

        lst = ui.find('certlist')
        for s in self.certs:
            lst.append(UI.DTR(
                UI.IconFont(iconfont='gen-certificate'),
                UI.Label(text=s['name']),
                UI.Label(text=', '.join(filter(None, s['assign']))),
                UI.HContainer(
                    UI.TipIcon(iconfont='gen-info', text='Information',
                        id='info/' + str(self.certs.index(s))),
                    UI.TipIcon(iconfont='gen-close', text='Delete',
                        id='del/' + str(self.certs.index(s)),
                        warning=('Are you sure you wish to remove this certificate? '
                            'SSL on all associated services will be disabled'), ),
                    ),
               ))

        lst = ui.find('certauth')
        if not self.cas:
            lst.append(UI.Button(text="Generate New", id="cagen"))
        for s in self.cas:
            exp = s['expiry']
            exp = exp[0:4] + '-' + exp[4:6] + '-' + exp[6:8] + ', ' + exp[8:10] + ':' + exp[10:12]
            lst.append(UI.FormLine(
                UI.HContainer(
                    UI.Label(text='Expires '+exp),
                    UI.TipIcon(iconfont='gen-download', text='Download',
                        id='cadl',
                        onclick='window.open("/certificates/dl", "_blank")'),
                    UI.TipIcon(iconfont='gen-close', text='Delete',
                        id='cadel/' + str(self.cas.index(s))),
                    ), text=s['name']
               ))

        if self._gen:
            ui.find('certcn').set('value', self.app.get_backend(IHostnameManager).gethostname().lower())
            self._wal, self._pal = self._cc.get_ssl_capable()
            alist, wlist, plist = [], [], []
            for cert in self.certs:
                for i in cert['assign']:
                    if i != '':
                        alist.append(i)
            if not 'Genesis SSL' in alist:
                ui.find('certassign').append(
                    UI.Checkbox(text='Genesis SSL', name='genesis', value='genesis', checked=False),
                )
            for x in self._wal:
                if not (x.name+' ('+x.stype+')') in alist:
                    ui.find('certassign').append(
                        UI.Checkbox(text=x.name, name='wassign[]', value=x.name, checked=False),
                    )
                    wlist.append(x)
            self._wal = wlist
            for x in self._pal:
                if not x.text in alist:
                    ui.find('certassign').append(
                        UI.Checkbox(text=x.text, name='passign[]', value=x.text, checked=False),
                    )
                    plist.append(x)
            self._pal = plist
        else:
            ui.remove('dlgGen')

        if self._cinfo:
            self._wal, self._pal = self._cc.get_ssl_capable()
            ui.find('certname').set('text', self._cinfo['name'])
            ui.find('domain').set('text', self._cinfo['domain'])
            ui.find('ikeytype').set('text', self._cinfo['keylength']+'-bit '+self._cinfo['keytype'])
            exp = self._cinfo['expiry']
            exp = exp[0:4] + '-' + exp[4:6] + '-' + exp[6:8] + ', ' + exp[8:10] + ':' + exp[10:12]
            ui.find('expires').set('text', exp)

            alist = []
            for cert in self.certs:
                if cert != self._cinfo:
                    for i in cert['assign']:
                        if i != '':
                            alist.append(i)

            if not 'Genesis SSL' in alist:
                if 'Genesis SSL' in self._cinfo['assign']:
                    ic, ict, show = 'gen-checkmark-circle', 'Assigned', 'd'
                else:
                    ic, ict, show = None, None, 'e'
                ui.find('certassign').append(
                    UI.DTR(
                        UI.IconFont(iconfont=ic, text=ict),
                        UI.IconFont(iconfont='gen-arkos-round'),
                        UI.Label(text='Genesis'),
                        UI.HContainer(
                            (UI.TipIcon(iconfont='gen-checkmark-circle',
                                text='Assign', id='ac/'+self._cinfo['name']+'/g') if show == 'e' else None),
                            (UI.TipIcon(iconfont='gen-close',
                                text='Unassign', id='uc/'+self._cinfo['name']+'/g',
                                warning=('Are you sure you wish to unassign this certificate? '
                                    'SSL on this service will be disabled, and you will need to '
                                    'reload Genesis for changes to take place.')) if show == 'd' else None),
                        ),
                    )
                )
            for x in self._wal:
                if not (x.name+' ('+x.stype+')') in alist:
                    if (x.name+' ('+x.stype+')') in self._cinfo['assign']:
                        ic, ict, show = 'gen-checkmark-circle', 'Assigned', 'd'
                    else:
                        ic, ict, show = None, None, 'e'
                    ui.find('certassign').append(
                        UI.DTR(
                            UI.IconFont(iconfont=ic, text=ict),
                            UI.IconFont(iconfont='gen-earth'),
                            UI.Label(text=x.name),
                            UI.HContainer(
                                (UI.TipIcon(iconfont='gen-checkmark-circle',
                                    text='Assign', id='ac/'+self._cinfo['name']+'/w/'+str(self._wal.index(x))) if show == 'e' else None),
                                (UI.TipIcon(iconfont='gen-close',
                                    text='Unassign', id='uc/'+self._cinfo['name']+'/w/'+str(self._wal.index(x)),
                                    warning=('Are you sure you wish to unassign this certificate? '
                                        'SSL on this service will be disabled.')) if show == 'd' else None),
                            ),
                        )
                    )
            for x in self._pal:
                if not x.text in alist:
                    if x.text in self._cinfo['assign']:
                        ic, ict, show = 'gen-checkmark-circle', 'Assigned', 'd'
                    else:
                        ic, ict, show = None, None, 'e'
                    ui.find('certassign').append(
                        UI.DTR(
                            UI.IconFont(iconfont=ic, text=ict),
                            UI.IconFont(iconfont=x.iconfont),
                            UI.Label(text=x.text),
                            UI.HContainer(
                                (UI.TipIcon(iconfont='gen-checkmark-circle',
                                    text='Assign', id='ac/'+self._cinfo['name']+'/p/'+str(self._pal.index(x))) if show == 'e' else None),
                                (UI.TipIcon(iconfont='gen-close',
                                    text='Unassign', id='uc/'+self._cinfo['name']+'/p/'+str(self._pal.index(x)),
                                    warning=('Are you sure you wish to unassign this certificate? '
                                        'SSL on this service will be disabled.')) if show == 'd' else None),
                            ),
                        )
                    )
        else:
            ui.remove('dlgInfo')

        if self._upload:
            ui.append('main', UI.DialogBox(
                UI.FormLine(UI.TextInput(name='certname'), text='Name'),
                UI.FormLine(UI.FileInput(id='certfile'), text='Certificate file'),
                UI.FormLine(UI.FileInput(id='keyfile'), text='Certificate keyfile'),
                UI.FormLine(UI.FileInput(id='chainfile'), text='Certificate chainfile', 
                    help='This is optional, only put it if you know you need one.'),
                id='dlgUpload', mp=True))

        return ui

    @url('^/certificates/dl$')
    def download(self, req, start_response):
        params = req['PATH_INFO'].split('/')[3:] + ['']
        filename = CertControl(self.app).get_cas()[0]['name']+'.pem'
        path = os.path.join('/etc/ssl/certs/genesis/ca', filename)
        f = open(path, 'rb')
        size = os.path.getsize(path)
        start_response('200 OK', [
            ('Content-length', str(size)),
            ('Content-Disposition', 'attachment; filename=%s' % filename)
        ])
        return f.read()

    @event('button/click')
    def on_click(self, event, params, vars = None):
        if params[0] == 'info':
            self._tab = 0
            self._cinfo = self.certs[int(params[1])]
        elif params[0] == 'gen':
            self._tab = 0
            self._gen = True
        elif params[0] == 'del':
            self._tab = 0
            self._cc.remove(self.certs[int(params[1])]['name'])
            self.put_message('info', 'Certificate successfully deleted')
        elif params[0] == 'ac' and params[2] == 'p':
            self._tab = 0
            self._cc.assign(self._cinfo['name'], 
                [('plugin', self._pal[int(params[3])])])
            self.put_message('info', '%s added to %s plugin' % (self._cinfo['name'], self._pal[int(params[3])].text))
            self._cinfo = None
        elif params[0] == 'ac' and params[2] == 'w':
            self._tab = 0
            self._cc.assign(self._cinfo['name'],
                [('webapp', self._wal[int(params[3])])])
            self.put_message('info', '%s added to %s webapp' % (self._cinfo['name'], self._wal[int(params[3])].name))
            self._cinfo = None
        elif params[0] == 'ac' and params[2] == 'g':
            self._tab = 0
            self._cc.assign(self._cinfo['name'], [[('genesis')]])
            self.put_message('info', '%s serving as Genesis certificate. Restart Genesis for changes to take effect' % self._cinfo['name'])
            self._cinfo = None
        elif params[0] == 'uc' and params[2] == 'p':
            self._tab = 0
            self._cc.unassign(self._cinfo['name'], 
                [('plugin', self._pal[int(params[3])])])
            self.put_message('info', '%s removed from %s plugin, and SSL disabled.' % (self._cinfo['name'], self._pal[int(params[3])].text))
            self._cinfo = None
        elif params[0] == 'uc' and params[2] == 'w':
            self._tab = 0
            self._cc.unassign(self._cinfo['name'],
                [('webapp', self._wal[int(params[3])])])
            self.put_message('info', '%s removed from %s webapp, and SSL disabled.' % (self._cinfo['name'], self._wal[int(params[3])].name))
            self._cinfo = None
        elif params[0] == 'uc' and params[2] == 'g':
            self._tab = 0
            self._cc.unassign(self._cinfo['name'], [[('genesis')]])
            self.put_message('info', 'Certificate removed and SSL disabled for Genesis. Reload Genesis for changes to take effect')
            self._cinfo = None
        elif params[0] == 'upl':
            self._tab = 0
            self._upload = True
        elif params[0] == 'cagen':
            self._tab = 1
            self._cc.create_authority(self.app.get_backend(IHostnameManager).gethostname().lower())
        elif params[0] == 'cadel':
            self._tab = 1
            self._cc.delete_authority(self.cas[int(params[1])])

    @event('form/submit')
    @event('dialog/submit')
    def on_submit(self, event, params, vars = None):
        if params[0] == 'dlgAdd':
            self._tab = 0
            if vars.getvalue('action', '') == 'OK':
                pass
        elif params[0] == 'dlgGen':
            self._tab = 0
            if vars.getvalue('action', '') == 'OK':
                if vars.getvalue('certname', '') == '':
                    self.put_message('err', 'Certificate name is mandatory')
                elif re.search('\.|-|`|\\\\|\/|[ ]', vars.getvalue('certname')):
                    self.put_message('err', 'Certificate name must not contain spaces, dots, dashes or special characters')
                elif vars.getvalue('certname', '') in [x['name'] for x in self.certs]:
                    self.put_message('err', 'You already have a certificate with that name.')
                elif len(vars.getvalue('certcountry', '')) != 2:
                    self.put_message('err', 'The country field must be a two-letter abbreviation')
                else:
                    lst = []
                    if vars.getvalue('genesis', '') == '1':
                        lst.append([('genesis')])
                    for i in range(0, len(self._wal)):
                        try:
                            if vars.getvalue('wassign[]')[i] == '1':
                                lst.append(('webapp', self._wal[i]))
                        except TypeError:
                            pass
                    for i in range(0, len(self._pal)):
                        try:
                            if vars.getvalue('passign[]')[i] == '1':
                                lst.append(('plugin', self._pal[i]))
                        except TypeError:
                            pass
                    cgw = CertGenWorker(self, vars.getvalue('certname'), vars, lst)
                    cgw.start()
            self._wal = []
            self._pal = []
            self._gen = False
        elif params[0] == 'dlgInfo':
            self._tab = 0
            self._cinfo = None
            self._wal = []
            self._pal = []
        elif params[0] == 'dlgUpload':
            self._tab = 0
            if vars.getvalue('action', '') == 'OK':
                if not vars.has_key('certfile') and not vars.has_key('keyfile'):
                    self.put_message('err', 'Please select at least a certificate and private key')
                elif not vars.has_key('certfile'):
                    self.put_message('err', 'Please select a certificate file')
                elif not vars.has_key('keyfile'):
                    self.put_message('err', 'Please select a key file')
                elif not vars.getvalue('certname', ''):
                    self.put_message('err', 'Must choose a certificate name')
                elif vars.getvalue('certname', '') in [x['name'] for x in self.certs]:
                    self.put_message('err', 'You already have a certificate with that name.')
                elif re.search('\.|-|`|\\\\|\/|[ ]', vars.getvalue('certname')):
                    self.put_message('err', 'Certificate name must not contain spaces, dots, dashes or special characters')
                else:
                    try:
                        self._cc.add_ext_cert(vars.getvalue('certname'), 
                            vars['certfile'].value, vars['keyfile'].value,
                            vars['chainfile'].value if vars.has_key('chainfile') else None)
                        self.put_message('info', 'Certificate %s installed' % vars.getvalue('certname'))
                    except Exception, e:
                        self.put_message('err', 'Couldn\'t add certificate: %s' % str(e[0]))
                        self.app.log.error('Couldn\'t add certificate: %s - Error: %s' % (str(e[0]), str(e[1])))
            self._upload = None
        elif params[0] == 'frmCertSettings':
            self._tab = 1
            if vars.getvalue('action', '') == 'OK':
                cfg = self.app.get_config(CertControl(self.app))
                cfg.keylength = vars.getvalue('keylength', '2048')
                cfg.keytype = vars.getvalue('keytype', 'RSA')
                cfg.save()
                self.put_message('info', 'Settings saved successfully')


class CertGenWorker(BackgroundWorker):
    def __init__(self, *args):
        BackgroundWorker.__init__(self, *args)

    def run(self, cat, name, vars, assign):
        cat.put_statusmsg('Generating a certificate and key...')
        try:
            CertControl(cat.app).gencert(name, vars, 
                cat.app.get_backend(IHostnameManager).gethostname().lower())
            cat.put_statusmsg('Assigning new certificate...')
            CertControl(cat.app).assign(name, assign)
        except Exception, e:
            cat.clr_statusmsg()
            cat.put_message('err', str(e))
            cat.app.log.error(str(e))
        cat.clr_statusmsg()
        cat.put_message('info', 'Certificate successfully generated')
