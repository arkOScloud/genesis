import Ember from "ember";
import EmberUploader from 'ember-uploader';
import ENV from "../../config/environment";
import toB64 from "../../utils/to-b64";
/* global CodeMirror */


export default Ember.ObjectController.extend({
  breadCrumb: {name: 'File Manager', icon: 'open folder outline'},
  sortBy: ['folder:desc', 'name'],

  // Default values
  showHidden: false,
  currentFolder: [],
  clipboard: [],
  currentPath: "",
  newFile: "",

  // Folder contents
  sortedFolder: Ember.computed.sort('filteredFolder', 'sortBy'),
  selectedItems: Ember.computed.filterBy('currentFolder', 'selected'),
  selectedItem: Ember.computed.alias('selectedItems.firstObject'),
  filteredFolder: Ember.computed.filter('currentFolder', function(i) {
    return (this.get("showHidden") === false) ? (i.hidden === false) : true;
  }).property('showHidden', 'currentFolder'),
  breadcrumbs: function() {
    var path = [];
    path.push({name: '/', path: '/'});
    this.get('currentPath').split('/').forEach(function(i) {
      if (i) {
        path.push({name: i, active: false, path: path[path.length-1]?path[path.length-1].path+"/"+i:"/"+i});
      }
    });
    path[path.length-1].active = true;
    return path;
  }.property('currentPath'),

  // Actions
  actions: {

    // General
    focusOpenInput: function() {
      Ember.$('.category.search.item input').focus();
    },
    clearOpenInput: function() {
      this.set('pathToOpen', '');
    },
    openModal: function(name) {
      Ember.$('.ui.' + name + '.modal').modal('show');
    },
    openSidebar: function(sidebarName) {
      var areOpen = Ember.$('.ui.sidebar').sidebar('is visible')
                    .any(function(i) {return i;});
      if (areOpen) {
        Ember.$('.ui.sidebar').sidebar('hide', function() {
          Ember.$('#' + sidebarName).sidebar('show', function() {
            Ember.$('#' + sidebarName + ' input').focus();
          });
        });
      } else {
        Ember.$('#' + sidebarName).sidebar('show', function() {
          Ember.$('#' + sidebarName + ' input').focus();
        });
      }
    },

    // File Menu
    newItem: function(name, isFolder) {
      var self = this;
      Ember.$('.ui.sidebar').sidebar('hide');
      Ember.$.ajax(`${ENV.APP.krakenHost}/api/files/${toB64(self.get('currentPath'))}`, {
        type: "POST",
        data: JSON.stringify({file: {folder: !!isFolder, name: name}}),
        contentType: 'application/json',
      })
        .done(function() {
          self.set("newItemName", "");
          self.send('refresh');
        })
        .fail(function(e) {
          if (e.status === 500) {
            self.transitionToRoute("error", e);
          } else if (e.errors) {
            e.errors.forEach(function(err) {
              self.notifications.new('error', err.detail);
            });
          }
        });
    },
    open: function(f) {
      var self = this;
      if (f.folder === false && f.binary === false) {
        this.send('previewFile', f);
        return false;
      } else if (f.folder === false) {
        this.notifications.new("error", "File cannot be opened.");
        return false;
      }
      Ember.$('#file-manager-segment').addClass('loading');
      Ember.$.getJSON(`${ENV.APP.krakenHost}/api/files/${f.id}`)
        .done(function(j) {
          if (j.files) {
            self.setProperties({currentPath: f.path, currentFolder: j.files});
          } else if (j.file && !!j.file.folder && !!j.file.binary) {
            self.send('previewFile', f);
          } else {
            self.notifications.new("error", "File cannot be opened.");
          }
        })
        .fail(function() {
          self.notifications.new("error", "Could not load folder.");
        })
        .always(function() {
          Ember.run.next(function() {
            Ember.$('#file-manager-segment').removeClass('loading');
          });
        });
    },
    openPath: function(p) {
      Ember.$('.ui.sidebar').sidebar('hide');
      this.send('open', {id: toB64(p), path: p});
    },
    previewFile: function(f) {
      var self = this;
      Ember.$('.ui.sidebar').sidebar('hide');
      Ember.$('#file-manager-segment').addClass('loading');
      Ember.$.getJSON(`${ENV.APP.krakenHost}/api/files/${f.id}?content=true`)
        .done(function(j) {
          self.set('editingFile', j.file);
          self.send('openEditingFileModal');
        })
        .fail(function(){
          self.notifications.new("error", "Could not load file.");
        })
        .always(function() {
          Ember.run.next(function() {
            Ember.$('#file-manager-segment').removeClass('loading');
          });
        });
    },
    deleteFiles: function() {
      var selection = this.get('selectedItems'),
          self = this;
      Ember.$('.ui.sidebar').sidebar('hide');
      selection.forEach(function(i) {
        Ember.$.ajax(`${ENV.APP.krakenHost}/api/files/${i.id}`, {type: "DELETE"})
          .done(function() {
            self.get('currentFolder').removeObject(i);
          });
      });
    },
    showProperties: function() {
      Ember.$('.ui.sidebar').sidebar('hide');
      if (this.get("selectedItems.length") === 1) {
        console.log(this.get("selectedItem"));
        this.send('openModal', 'file-info');
      } else {
        this.notifications.new("error", "Can only check on properties of one item at a time");
      }
    },

    // Edit Menu
    copy: function() {
      Ember.$('.ui.sidebar').sidebar('hide');
      this.get('clipboard').clear().pushObjects(this.get('selectedItems'));
      this.notifications.new("success", `${this.get('selectedItems').get('length')} item(s) added to clipboard`);
      this.get('currentFolder').setEach('selected', false);
    },
    paste: function() {
      var self = this;
      Ember.$('.ui.sidebar').sidebar('hide');
      this.get('clipboard').forEach(function(i) {
        i.newdir = self.get('currentPath');
        i.operation = "copy";
        Ember.$.ajax(`${ENV.APP.krakenHost}/api/files/${toB64(i.newdir)}`, {
          type: "PUT",
          data: JSON.stringify({file: i}),
          contentType: 'application/json'
        })
          .done(function(j) {
            self.get('currentFolder').pushObject(j.file);
          })
          .fail(function(e) {
            if (e.status === 500) {
              self.transitionToRoute("error", e);
            } else if (e.errors) {
              e.errors.forEach(function(err) {
                self.notifications.new('error', err.detail);
              });
            }
          });
      });
    },
    removeFromClipboard: function(item) {
      this.get('clipboard').removeObject(item);
    },
    clearClipboard: function() {
      Ember.$('.ui.sidebar').sidebar('hide');
      this.get('clipboard').clear();
    },
    selectAll: function() {
      this.get('currentFolder').setEach('selected', true);
    },
    deselectAll: function() {
      this.get('currentFolder').setEach('selected', false);
    },

    // View Menu
    refresh: function() {
      this.send('openPath', this.get('currentPath'));
    },
    toggleHidden: function() {
      this.toggleProperty("showHidden");
    },

    // Tools Menu
    addToDownloads: function() {
      var self = this;
      Ember.$('.ui.sidebar').sidebar('hide');
      this.get('selectedItems').forEach(function(i){
        var newShare = self.store.createRecord('share', {
          path: i.path,
          expires: false
        });
        var promise = newShare.save();
        promise.then(function(){}, function(e){
          if (e.status === 500) {
            self.transitionToRoute("error", e);
          } else if (e.errors) {
            e.errors.forEach(function(err) {
              self.notifications.new('error', err.detail);
            });
          }
          newShare.deleteRecord();
        });
      });
      this.send('deselectAll');
      this.send('openModal', 'download-files');
    },

    // Modal Actions
    saveProperties: function() {
      var self = this,
          poct = "0o",
          file = this.get("selectedItem"),
          p = this.get("selectedItem.perms");
      poct += String((p.user.read?4:0)+(p.user.write?2:0)+(p.user.execute?1:0));
      poct += String((p.group.read?4:0)+(p.group.write?2:0)+(p.group.execute?1:0));
      poct += String((p.all.read?4:0)+(p.all.write?2:0)+(p.all.execute?1:0));
      file = JSON.parse(JSON.stringify(file));
      file.perms.oct = poct;
      file.operation = "props";
      Ember.$.ajax(`${ENV.APP.krakenHost}/api/files/${file.id}`, {
        type: "PUT",
        data: JSON.stringify({file: file}),
        contentType: 'application/json'
      })
        .done(function() {
          self.notifications.new("success", "Permissions changed successfully");
        })
        .fail(function(e) {
          if (e.status === 500) {
            self.transitionToRoute("error", e);
          } else if (e.errors) {
            e.errors.forEach(function(err) {
              self.notifications.new('error', err.detail);
            });
          }
          self.notifications.new("error", e.responseJSON.message);
        });
    },
    openEditingFileModal: function() {
      var self = this;
      var file = this.get('editingFile');
      if (this.get("cm")) {
        this.get("cm").toTextArea();
      }
      Ember.$('.ui.edit-file.modal').modal('show', function() {
        var cm = CodeMirror.fromTextArea(document.getElementById("editArea"), {
          lineNumbers: true,
          mode: file.mimetype ? file.mimetype : "shell"
        });
        cm.on('update', function() {
          self.set("editingFile.content", cm.getValue());
        });
        self.set('cm', cm);
      });
    },
    saveEditingFile: function() {
      var self = this,
          file = this.get("editingFile");
      Ember.$.ajax(`${ENV.APP.krakenHost}/api/files/${file.id}`, {
        type: "PUT",
        data: JSON.stringify({file:{path:file.path,data:file.content,operation:"edit"}}),
        contentType: 'application/json'
      })
        .done(function() {
          self.notifications.new("success", "File saved successfully");
        })
        .fail(function(e) {
          if (e.status === 500) {
            self.transitionToRoute("error", e);
          } else if (e.errors) {
            e.errors.forEach(function(err) {
              self.notifications.new('error', err.detail);
            });
          }
        });
    },
    saveUploadedFile: function(){
      var self = this,
          cp   = this.get("currentPath") || "/";
      var uploader = EmberUploader.Uploader.create({
        url: `${ENV.APP.krakenHost}/api/files/${toB64(cp)}`
      });
      var promise = uploader.upload(Ember.$('input[name="file"]')[0].files);
      promise.then(function(j){
        j.files.forEach(function(i) {
          self.get("currentFolder").pushObject(i);
        });
      }, function(e){
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        } else if (e.errors) {
          e.errors.forEach(function(err) {
            self.notifications.new('error', err.detail);
          });
        }
      });
    },
    removeDownload: function(dl) {
      dl.destroyRecord();
    }
  }
});
