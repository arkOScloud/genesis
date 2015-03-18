Genesis.FilesController = Ember.ObjectController.extend({
  currentFolder: [],
  clipboard: [],
  currentPath: "",
  showHidden: true,
  newFile: "",
  filteredFolder: Ember.computed.filter('currentFolder', function(i) {
    if (this.get("showHidden")==false) {
      return i.hidden==false;
    } else {
      return true;
    };
  }).property('showHidden', 'currentFolder'),
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
      var data = $.getJSON(Genesis.Config.krakenHost+'/files/'+Genesis.toB64(f.path), function(j) {
        self.set('currentPath', f.path);
        self.set('currentFolder', j.files);
      });
    },
    openPath: function(p) {
      this.send('open', {path: p});
    },
    newFile: function() {
      var fn = this.get("newFile");
      $.ajax({
        url: Genesis.Config.krakenHost+'/files/'+Genesis.toB64(f.currentPath),
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
        url: Genesis.Config.krakenHost+'/files/'+Genesis.toB64(f.currentPath),
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
      this.get('selectedItems').forEach(function(i) {
        self.get('clipboard').pushObject(i);
      });
      this.message.success(this.get('selectedItems').get('length')+" item(s) added to clipboard");
      this.get('currentFolder').setEach('selected', false);
    },
    menu: function() {
      console.log('Menu called');
    },
    toggleHidden: function() {
      this.set("showHidden", !this.get("showHidden"));
    }
  }
});
