import Ember from "ember";
import ENV from "../config/environment";
import toB64 from "../utils/to-b64";
import {showFade, showLoader, hideLoader, hideFade} from "../utils/loading";


export default Ember.ObjectController.extend({
  currentFolder: [],
  clipboard: [],
  currentPath: "",
  showHidden: true,
  newFile: "",
  sortBy: ['folder:desc', 'name'],
  filteredFolder: Ember.computed.filter('currentFolder', function(i) {
    if (this.get("showHidden") === false) {
      return i.hidden === false;
    } else {
      return true;
    }
  }).property('showHidden', 'currentFolder'),
  sortedFolder: Ember.computed.sort('filteredFolder', 'sortBy'),
  selectedItems: Ember.computed.filterBy('currentFolder', 'selected'),
  breadcrumbs: function() {
    var path = [];
    this.get('currentPath').split('/').forEach(function(i) {
        if (i) {
          path.push({name: i, path: path[path.length-1]?path[path.length-1].path+"/"+i:"/"+i});
        }
    });
    return path;
  }.property('currentPath'),
  openPath: function(path) {
    this.send('openPath', path);
  },
  actions: {
    refresh: function() {
      this.send('openPath', this.get('currentPath'));
    },
    open: function(f) {
      var self = this;
      if (f.folder === false && f.binary === false) {
        this.send('openFile', f);
        return false;
      } else if (f.folder === false) {
        this.message.danger("File cannot be opened.");
        return false;
      }
      showFade();
      showLoader(function(){
        var fo = Ember.$.getJSON(ENV.APP.krakenHost+'/api/files/'+f.id, function(j) {
          if (j.file && j.file.folder === false && j.file.binary === false) {
            self.send('openFile', f);
            return false;
          } else if (j.file && j.file.folder === false) {
            self.message.danger("File cannot be opened.");
            hideLoader();
            hideFade();
            return false;
          }
          self.set('currentPath', f.path);
          self.set('currentFolder', j.files);
          hideLoader();
          hideFade();
        });
        fo.fail(function(){
          hideLoader();
          hideFade();
          self.message.danger("Could not load folder.");
        });
      });
    },
    openPath: function(p) {
      this.send('open', {id: toB64(p), path: p});
    },
    openFile: function(f) {
      var self = this;
      showFade();
      showLoader(function(){
        var fo = Ember.$.getJSON(ENV.APP.krakenHost+'/api/files/'+f.id+'?content=true', function(j) {
          hideLoader();
          hideFade();
          self.send('showModal', 'file/notepad', j.file);
        });
        fo.fail(function(){
          hideLoader();
          hideFade();
          self.message.danger("Could not load file.");
        });
      });
    },
    newFile: function() {
      var self = this;
      var fn = this.get("newFile");
      Ember.$.ajax({
        url: ENV.APP.krakenHost+'/api/files/'+toB64(self.get('currentPath')),
        type: "POST",
        data: JSON.stringify({new: "file", name: fn}),
        contentType: 'application/json',
        processData: false,
        error: function(e) {
          if (e.status === 500) {
            self.transitionToRoute("error", e);
          }
        }
      });
      this.set("newFile", "");
      this.send('refresh');
    },
    newFolder: function() {
      var self = this;
      var fn = this.get("newFile");
      Ember.$.ajax({
        url: ENV.APP.krakenHost+'/api/files/'+toB64(self.get('currentPath')),
        type: "POST",
        data: JSON.stringify({new: "folder", name: fn}),
        contentType: 'application/json',
        processData: false,
        error: function(e) {
          if (e.status === 500) {
            self.transitionToRoute("error", e);
          }
        }
      });
      this.set("newFile", "");
      this.send('refresh');
    },
    selectAll: function() {
      this.get('currentFolder').setEach('selected', true);
    },
    deselectAll: function() {
      this.get('currentFolder').setEach('selected', false);
    },
    copy: function() {
      var self = this;
      self.set('clipboard', []);
      this.get('selectedItems').forEach(function(i) {
        self.get('clipboard').pushObject(i);
      });
      this.message.success(this.get('selectedItems').get('length')+" item(s) added to clipboard");
      this.get('currentFolder').setEach('selected', false);
    },
    paste: function() {
      var self = this;
      this.get('clipboard').forEach(function(i) {
        i.newdir = self.get('currentPath');
        i.operation = "copy";
        Ember.$.ajax({
          url: ENV.APP.krakenHost+'/api/files/'+toB64(i.newdir),
          type: "PUT",
          data: JSON.stringify({file: i}),
          contentType: 'application/json',
          processData: false,
          success: function(j) {
            self.get('currentFolder').pushObject(j.file);
          },
          error: function(e) {
            if (e.status === 500) {
              self.transitionToRoute("error", e);
            }
          }
        });
      });
    },
    addToDownloads: function() {
      var self = this;
      this.get('selectedItems').forEach(function(i){
        var newShare = self.store.createRecord('share', {
          path: i.path,
          expires: false
        });
        var promise = newShare.save();
        promise.then(function(){}, function(e){
          if (e.status === 500) {
            self.transitionToRoute("error", e);
          }
          newShare.deleteRecord();
        });
      });
      this.send('deselectAll');
      this.send('showModal', 'file/downloads', this.get('model'));
    },
    properties: function() {
      if (this.get("selectedItems.length") === 1) {
        this.send('showModal', 'file/properties', this.get('selectedItems')[0]);
      } else {
        this.message.danger("Can only check on properties of one item at a time");
      }
    },
    toggleHidden: function() {
      this.set("showHidden", !this.get("showHidden"));
    }
  }
});
