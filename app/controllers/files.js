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
    if (this.get("showHidden")==false) {
      return i.hidden==false;
    } else {
      return true;
    };
  }).property('showHidden', 'currentFolder'),
  sortedFolder: Ember.computed.sort('filteredFolder', 'sortBy'),
  selectedItems: Ember.computed.filterBy('currentFolder', 'selected'),
  breadcrumbs: function() {
    var path = [];
    this.get('currentPath').split('/').forEach(function(i) {
        if (i) path.push({name: i, path: path[path.length-1]?path[path.length-1].path+"/"+i:"/"+i});
    });
    return path;
  }.property('currentPath'),
  actions: {
    refresh: function() {
      this.send('openPath', this.get('currentPath'));
    },
    open: function(f) {
      var self = this;
      showFade();
      showLoader(function(){
        var fo = $.getJSON(ENV.APP.krakenHost+'/files/'+f.id, function(j) {
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
    newFile: function() {
      var fn = this.get("newFile");
      $.ajax({
        url: ENV.APP.krakenHost+'/files/'+toB64(f.currentPath),
        type: "POST",
        data: JSON.stringify({new: "file", name: fn}),
        contentType: 'application/json',
        processData: false
      });
      this.set("newFile", "");
      this.send('refresh');
    },
    newFolder: function() {
      var fn = this.get("newFile");
      $.ajax({
        url: ENV.APP.krakenHost+'/files/'+toB64(f.currentPath),
        type: "POST",
        data: JSON.stringify({new: "folder", name: fn}),
        contentType: 'application/json',
        processData: false
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
        $.ajax({
          url: ENV.APP.krakenHost+'/files/'+toB64(i.newdir),
          type: "PUT",
          data: JSON.stringify({file: i}),
          contentType: 'application/json',
          processData: false,
          success: function(j) {
            self.get('currentFolder').pushObject(j.file);
          }
        });
      });
    },
    toggleHidden: function() {
      this.set("showHidden", !this.get("showHidden"));
    }
  }
});
