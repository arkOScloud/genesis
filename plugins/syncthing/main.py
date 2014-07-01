from genesis.api import *
from genesis.ui import *
from genesis.utils import *
from genesis import apis

import backend


class SyncthingPlugin(apis.services.ServiceControlPlugin):
    text = 'File Shares BETA'
    iconfont = 'gen-loop-2'
    folder = 'servers'
    
    def on_session_start(self):
        self._cfg = backend.SyncthingConfig(self.app)
        self._mgr = backend.SyncthingControl(self.app)
        self._cfg.load()

    def on_init(self):
        self.repos = self._mgr.get_repos()
        self.nodes = self._mgr.get_nodes()

    def get_main_ui(self):
        ui = self.app.inflate('syncthing:main')
        
        for x in self.repos:
            ui.append('repos', UI.TblBtn(
                id='erepo/'+str(self.repos.index(x)),
                icon="gen-folder",
                name=x["id"],
                subtext="Repository"
                ))
        ui.append('repos', UI.TblBtn(
            id="arepo",
            icon="gen-plus-circle",
            name="Add New Repository"
            ))

        for x in self.nodes:
            ui.append('nodes', UI.TblBtn(
                id='enode/'+str(self.nodes.index(x)),
                icon="gen-code",
                name=x["name"],
                subtext="%sNode" % ("Primary " if x["myid"] else "")
                ))
        ui.append('nodes', UI.TblBtn(
            id="anode",
            icon="gen-plus-circle",
            name="Add New Node"
            ))

        if self._editrepo:
            for x in self.nodes:
                if not x["myid"]:
                    ui.append("rnodesph", 
                        UI.FormLine(
                            UI.Checkbox(name="rnodes[]", value=x["name"], text=x["name"], 
                                selected=(x["id"] in self._editrepo["nodes"]) if self._editrepo != "new" else False),
                            checkbox="True"
                        )
                    )
            if self._editrepo != "new":
                dlg = ui.find("dlgEditRepo")
                dlg.set("title", "Edit Repository")
                dlg.set("miscbtn", "Delete")
                dlg.set("miscbtnid", "drepo/%s" % self.repos.index(self._editrepo))
                dlg.set("miscbtnstyle", "danger")
                dlg.set("miscbtnwarn", "Are you sure you want to delete %s? This will not remove the local folder and data." % self._editrepo["id"])
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
                dlg.set("title", "Edit Node")
                if not self._editnode["myid"]:
                    dlg.set("miscbtn", "Delete")
                    dlg.set("miscbtnid", "dnode/%s" % self.nodes.index(self._editnode))
                    dlg.set("miscbtnstyle", "danger")
                    dlg.set("miscbtnwarn", "Are you sure you want to delete your connection to %s?" % self._editnode["name"])
                ui.find("nnidph").set("text", '-'.join([self._editnode["id"][i:i+6] for i in range(0, len(self._editnode["id"]), 6)]))
                ui.find("nname").set("value", self._editnode["name"])
                ui.find("naddr").set("value", self._editnode["address"])
                ui.find("naddr").set("disabled", True)
        else:
            ui.remove("dlgEditNode")

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
        elif params[0] == 'dnode':
            self._mgr.del_node(self.nodes[int(params[1])]["name"])
            self.put_message("success", "Node connection deleted successfully")
            self._editnode = False

    @event('dialog/submit')
    @event('form/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgNodeID':
            self._nodeid = False
        elif params[0] == 'dlgEditNode':
            if vars.getvalue('action', '') == 'OK':
                if self._editnode == "new":
                    if not vars.getvalue("nnid", ""):
                        self.put_message("err", "Must enter your corresponding node ID")
                    elif not vars.getvalue("nname", ""):
                        self.put_message("err", "Must choose a repository name")
                    elif not vars.getvalue("naddr", ""):
                        self.put_message("err", "Must choose addresses/addressing")
                    else:
                        self._mgr.add_node(vars.getvalue("nname", ""),
                            vars.getvalue("nnid", ""), vars.getvalue("naddr", ""))
                        self.put_message("success", "Node added successfully")
                else:
                    if not vars.getvalue("nname", ""):
                        self.put_message("err", "Must choose a repository name")
                    elif vars.getvalue("nname", "") != self._editnode["name"]:
                        self._mgr.edit_node(self._editnode["name"], vars.getvalue("nname", ""))
                        self.put_message("success", "Node edited successfully")
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
                        self.put_message("err", "Must enter a valid path for this repository")
                    elif not vars.getvalue("rid", ""):
                        self.put_message("err", "Must enter a valid repository name")
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
                        self.put_message("err", "Must enter a valid path for this repository")
                    else:
                        self._mgr.edit_repo(self._editrepo["id"], 
                            vars.getvalue("rpath", "~/Sync"),
                            vars.getvalue("rrmast", "0")=="1",
                            vars.getvalue("rignp", "0")=="1",
                            vars.getvalue("rvnum", "1") if vars.getvalue("rvers", "0") == "1" else False,
                            nodes)
            self._editrepo = False
