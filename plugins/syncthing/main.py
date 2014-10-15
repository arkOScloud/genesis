from genesis.api import *
from genesis.ui import *
from genesis.utils import *
from genesis import apis

import backend


class SyncthingPlugin(apis.services.ServiceControlPlugin):
    text = 'File Sync BETA'
    iconfont = 'gen-loop-2'
    folder = 'servers'
    
    def on_session_start(self):
        self._cfg = backend.SyncthingConfig(self.app)
        self._mgr = backend.SyncthingControl(self.app)
        self._cfg.load()
        # Generate points of interest
        fs = apis.poicontrol(self.app)
        exc = []
        r = self._mgr.get_repos()
        for x in r:
            if x["directory"] in [y.path for y in fs.get_pois()]:
                exc.append(x["directory"])
        for x in r:
            if not x["directory"] in exc:
                fs.add(x["id"], 'fsync', x["directory"], 'fsync', 'gen-folder', False)

    def on_init(self):
        self.repos = self._mgr.get_repos()
        self.nodes = self._mgr.get_nodes()

    def get_main_ui(self):
        ui = self.app.inflate('syncthing:main')

        if not self._cfg.ready:
            self.put_message("info", "Syncthing is setting itself up in the background. Please make sure it is running via the Status button, and come back in a few minutes...")
            ui.remove("nid")
            ui.remove("settings")
            ui.remove("repos")
            ui.remove("nodes")
            self._cfg.load()
        else:
            for x in self.repos:
                ui.append('repos', UI.TblBtn(
                    id='erepo/'+str(self.repos.index(x)),
                    icon="gen-folder",
                    name=x["id"],
                    subtext="Folder"
                    ))
            ui.append('repos', UI.TblBtn(
                id="arepo",
                icon="gen-plus-circle",
                name="Add New Folder"
                ))

            for x in self.nodes:
                ui.append('nodes', UI.TblBtn(
                    id='enode/'+str(self.nodes.index(x)),
                    icon="gen-code",
                    name=x["name"],
                    subtext="%sDevice" % ("Primary " if x["myid"] else "")
                    ))
            ui.append('nodes', UI.TblBtn(
                id="anode",
                icon="gen-plus-circle",
                name="Add New Device"
                ))

        if self._editrepo:
            for x in self.nodes:
                ui.append("rnodesph", 
                    UI.FormLine(
                        UI.Checkbox(name="rnodes[]", value=x["name"], text=x["name"], 
                            checked=(x["id"] in self._editrepo["nodes"]) if self._editrepo != "new" else False),
                        checkbox="True"
                    )
                )
            if self._editrepo != "new":
                dlg = ui.find("dlgEditRepo")
                dlg.set("title", "Edit Folder")
                dlg.set("miscbtn", "Delete")
                dlg.set("miscbtnid", "drepo/%s" % self.repos.index(self._editrepo))
                dlg.set("miscbtnstyle", "danger")
                dlg.set("miscbtnwarn", "Are you sure you want to delete %s? This will not remove the local copy of your data." % self._editrepo["id"])
                ui.find("rid").set("value", self._editrepo["id"])
                ui.find("rid").set("disabled", True)
                ui.find("rpath").set("value", self._editrepo["directory"])
                ui.find("rrmast").set("checked", self._editrepo["ro"])
                ui.find("rignp").set("checked", self._editrepo["ignorePerms"])
                ui.find("rvers").set("checked", self._editrepo["versioning"] != False)
                ui.find("rvnum").set("value", self._editrepo["versioning"] if self._editrepo["versioning"] else "")
        else:
            ui.remove("dlgEditRepo")

        if self._editnode:
            if self._editnode == "new":
                ui.remove("nnid")
                ui.append("nnidfl", UI.TextInput(name="nnid", id="nnid"))
            else:
                dlg = ui.find("dlgEditNode")
                dlg.set("title", "Edit Device")
                if not self._editnode["myid"]:
                    dlg.set("miscbtn", "Delete")
                    dlg.set("miscbtnid", "dnode/%s" % self.nodes.index(self._editnode))
                    dlg.set("miscbtnstyle", "danger")
                    dlg.set("miscbtnwarn", "Are you sure you want to delete your connection to %s?" % self._editnode["name"])
                ui.find("nnidph").set("text", '-'.join([self._editnode["id"][i:i+6] for i in range(0, len(self._editnode["id"]), 6)]) if not '-' in self._editnode["id"] else self._editnode["id"])
                ui.find("nname").set("value", self._editnode["name"])
                ui.find("naddr").set("value", self._editnode["address"])
                ui.find("naddr").set("disabled", True)
        else:
            ui.remove("dlgEditNode")

        if self._settings:
            ui.find("spla").set("value", self._cfg.getopt("listenAddress"))
            ui.find("sorl").set("value", self._cfg.getopt("maxSendKbps"))
            ui.find("srsi").set("value", self._cfg.getopt("rescanIntervalS"))
            ui.find("srci").set("value", self._cfg.getopt("reconnectionIntervalS"))
            ui.find("smor").set("value", self._cfg.getopt("parallelRequests"))
            ui.find("sfcr").set("value", self._cfg.getopt("maxChangeKbps"))
            ui.find("sldp").set("value", self._cfg.getopt("localAnnouncePort"))
            ui.find("sgla").set("value", self._cfg.config.find("./gui/address").text)
            ui.find("sgau").set("value", self._cfg.config.find("./gui/user").text if self._cfg.config.find("./gui/user") else "")
            ui.find("sldi").set("checked", self._cfg.getopt("localAnnounceEnabled")=="true")
            ui.find("sgdi").set("checked", self._cfg.getopt("globalAnnounceEnabled")=="true")
            ui.find("ssbw").set("checked", self._cfg.getopt("startBrowser")=="true")
            ui.find("supp").set("checked", self._cfg.getopt("upnpEnabled")=="true")
            ui.find("saur").set("checked", self._cfg.getopt("urAccepted")=="1")
        else:
            ui.remove("dlgSettings")

        if self._nodeid:
            nid = '-'.join([self._cfg.myid[i:i+6] for i in range(0, len(self._cfg.myid), 6)])
            ui.find("nodeidph").set("text", nid)
        else:
            ui.remove("dlgNodeID")

        return ui

    @event('button/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'nid':
            self._nodeid = True
        elif params[0] == 'anode':
            self._editnode = "new"
        elif params[0] == 'arepo':
            self._editrepo = "new"
        elif params[0] == 'erepo':
            self._editrepo = self.repos[int(params[1])]
        elif params[0] == 'enode':
            self._editnode = self.nodes[int(params[1])]
        elif params[0] == 'drepo':
            self._mgr.del_repo(self.repos[int(params[1])]["id"])
            self.put_message("success", "Folder deleted successfully")
            self._editrepo = False
        elif params[0] == 'dnode':
            self._mgr.del_node(self.nodes[int(params[1])]["name"])
            self.put_message("success", "Device connection deleted successfully")
            self._editnode = False
        elif params[0] == 'settings':
            self._settings = True

    @event('dialog/submit')
    @event('form/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgNodeID':
            self._nodeid = False
        elif params[0] == 'dlgSettings':
            if vars.getvalue('action', '') == 'OK':
                self._cfg.setopt("listenAddress", vars.getvalue("spla", ""))
                self._cfg.setopt("maxSendKbps", vars.getvalue("sorl", ""))
                self._cfg.setopt("rescanIntervalS", vars.getvalue("srsi", ""))
                self._cfg.setopt("reconnectionIntervalS", vars.getvalue("srci", ""))
                self._cfg.setopt("parallelRequests", vars.getvalue("smor", ""))
                self._cfg.setopt("maxChangeKbps", vars.getvalue("sfcr", ""))
                self._cfg.setopt("localAnnouncePort", vars.getvalue("sldp", ""))
                self._cfg.setopt("localAnnounceEnabled", "true" if vars.getvalue("sldi", "0") == "1" else "false")
                self._cfg.setopt("globalAnnounceEnabled", "true" if vars.getvalue("sgdi", "0") == "1" else "false")
                self._cfg.setopt("startBrowser", "true" if vars.getvalue("ssbw", "0") == "1" else "false")
                self._cfg.setopt("upnpEnabled", "true" if vars.getvalue("supp", "0") == "1" else "false")
                self._cfg.setopt("urAccepted", "1" if vars.getvalue("saur", "0") == "1" else "-1")
                self._cfg.save()
                self.put_message("success", "Settings saved successfully")
            self._settings = False
        elif params[0] == 'dlgEditNode':
            if vars.getvalue('action', '') == 'OK':
                if self._editnode == "new":
                    if not vars.getvalue("nnid", ""):
                        self.put_message("err", "Must enter your corresponding device ID")
                    elif not vars.getvalue("nname", ""):
                        self.put_message("err", "Must choose a folder name")
                    elif not vars.getvalue("naddr", ""):
                        self.put_message("err", "Must choose addresses/addressing")
                    else:
                        self._mgr.add_node(vars.getvalue("nname", ""),
                            vars.getvalue("nnid", ""), vars.getvalue("naddr", ""))
                        self.put_message("success", "Device added successfully")
                else:
                    if not vars.getvalue("nname", ""):
                        self.put_message("err", "Must choose a folder name")
                    elif vars.getvalue("nname", "") != self._editnode["name"]:
                        self._mgr.edit_node(self._editnode["name"], vars.getvalue("nname", ""))
                        self.put_message("success", "Device edited successfully")
            self._editnode = False
        elif params[0] == 'dlgEditRepo':
            if vars.getvalue('action', '') == 'OK':
                nodes = []
                for i in range(0, len(self.nodes)):
                    try:
                        if vars.getvalue('rnodes[]')[i] == '1':
                            nodes.append(self.nodes[i]["name"])
                    except TypeError:
                        pass
                if self._editrepo == "new":
                    if not vars.getvalue("rpath", ""):
                        self.put_message("err", "Must enter a valid path for this folder")
                    elif not vars.getvalue("rid", ""):
                        self.put_message("err", "Must enter a valid folder name")
                    elif vars.getvalue("rvnum", "") and not vars.getvalue("rvers", ""):
                        self.put_message("err", "Must enter a number of files to keep versioned")
                    else:
                        self._mgr.add_repo(vars.getvalue("rid", ""),
                            vars.getvalue("rpath", "~/Sync"),
                            vars.getvalue("rrmast", "0")=="1",
                            vars.getvalue("rignp", "0")=="1",
                            vars.getvalue("rvnum", "1") if vars.getvalue("rvers", "0") == "1" else False,
                            nodes
                            )
                else:
                    if not vars.getvalue("rpath", ""):
                        self.put_message("err", "Must enter a valid path for this folder")
                    else:
                        self._mgr.edit_repo(self._editrepo["id"], 
                            vars.getvalue("rpath", "~/Sync"),
                            vars.getvalue("rrmast", "0")=="1",
                            vars.getvalue("rignp", "0")=="1",
                            vars.getvalue("rvnum", "1") if vars.getvalue("rvers", "0") == "1" else False,
                            nodes)
            self._editrepo = False
