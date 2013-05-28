from genesis.api import *
from genesis.ui import *

from api import Manager
from os import path


class RecoveryPlugin(CategoryPlugin, URLHandler):
    text = 'Recovery'
    iconfont = 'gen-history'
    folder = None

    def on_init(self):
        self.manager = Manager(self.app)
        self.providers = self.app.grab_plugins(IConfigurable)
        self.providers = sorted(self.providers, key=lambda x: x.name)
        if not self._current:
            self._current = self.providers[0].id
            self._current_name = self.providers[0].name

    def get_ui(self):
        ui = self.app.inflate('recovery:main')

        provs = ui.find('provs')

        for p in self.providers:
            provs.append(
                    UI.ListItem(
                        UI.Label(text=p.name),
                        id=p.id,
                        active=p.id==self._current
                    )
                  )

        backs = ui.find('backs')

        for rev in self.manager.list_backups(self._current):
            backs.append(
                UI.DTR(
                    UI.Label(text=rev.revision),
                    UI.Label(text=rev.date),
                    UI.DTC(
                        UI.HContainer(
                            UI.TipIcon(
                                text='Recover',
                                iconfont="gen-folder-upload",
                                id='restore/%s/%s'%(self._current,rev.revision),
                                warning='Restore configuration of %s as of %s (rev %s)'%(
                                        self._current,
                                        rev.date,
                                        rev.revision
                                    )
                            ),
                            UI.TipIcon(
                                text='Download',
                                iconfont="gen-download",
                                onclick="window.open('/recovery/%s/%s', '_blank')" % (self._current,rev.revision),
                                id='download'
                            ),
                            UI.TipIcon(
                                text='Drop',
                                iconfont='gen-folder-minus',
                                id='drop/%s/%s'%(self._current,rev.revision),
                                warning='Delete backed up configuration of %s as of %s (rev %s)'%(
                                        self._current,
                                        rev.date,
                                        rev.revision
                                    )
                            ),
                            spacing=0
                        ),
                        width=0,
                    )
                )
            )

        ui.find('btnBackup').set('text', 'Backup %s'%self._current_name)
        ui.find('btnBackup').set('id', 'backup/%s'%self._current)
        return ui

    @url('^/recovery/.*$')
    def get_backup(self, req, start_response):
        params = req['PATH_INFO'].split('/')[1:] + ['']
        filename = '/var/backups/genesis/' + params[1] + '/' + params[2] + '.tar.gz'
        f = open(filename, 'rb')
        size = path.getsize(filename)

        fw = open('/home/jacob/test', 'r+')
        fw.write("Test")
        fw.close()

        start_response('200 OK', [
            ('Content-type', 'application/gzip'),
            ('Content-length', str(size)),
            ('Content-Disposition', 'attachment; filename=' + params[1] + '-' + params[2] + '.tar.gz')
        ])
        return f.read()

    @event('button/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'backup':
            p = self.manager.find_provider(params[1])
            try:
                self.manager.backup(p)
                self.put_message('info', 'Stored backup for %s.' % p.name)
            except:
                self.put_message('err', 'Failed to backup %s.' % p.name)
        if params[0] == 'backupall':
            errs = self.manager.backup_all()
            if errs != []:
                self.put_message('err', 'Backup failed for %s.' % ', '.join(errs))
            else:
                self.put_message('info', 'Stored full backup')
        if params[0] == 'restore':
            p = self.manager.find_provider(params[1])
            try:
                self.manager.restore(p, params[2])
                self.put_message('info', 'Restored configuration of %s (rev %s).' % (p.name, params[2]))
            except:
                self.put_message('err', 'Failed to recover %s.' % p.name)
        if params[0] == 'drop':
            try:
                self.manager.delete_backup(params[1], params[2])
                self.put_message('info', 'Deleted backup rev %s for %s.' % (params[2], params[1]))
            except:
                self.put_message('err', 'Failed to delete backup rev %s for %s.' % (params[2], params[1]))

    @event('listitem/click')
    def on_list_click(self, event, params, vars=None):
        for p in self.providers:
            if p.id == params[0]:
                self._current = p.id
                self._current_name = p.name
