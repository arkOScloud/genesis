Genesis.FilesRoute = Ember.Route.extend({
  model: function() {
    return Ember.RSVP.hash({
      POIs: this.get('store').find('point')
    });
  },
  setupController: function(controller, model) {
    this._super();
    controller.set('model', model);
    if (!this.get("currentPath")) {
        this.set('currentPath', "/");
        var data = $.getJSON(Genesis.Config.krakenHost+'/files/'+Genesis.toB64("/"), function(j) {
          controller.set('currentFolder', j.files);
        });
    };
  },
  actions: {
    removeFromClipboard: function(item) {
      this.get('controller.clipboard').removeObject(item);
    },
    clearClipboard: function() {
      this.get('controller.clipboard').clear();
    },
    delete: function() {
      var selection = this.get('controller.selectedItems'),
          self = this;
      selection.forEach(function(i) {
        $.ajax({
          url: Genesis.Config.krakenHost+'/files/'+Genesis.toB64(i.path),
          type: "DELETE",
          success: function(){
            self.get('controller.currentFolder').removeObject(i);
          }
        })
      });
    }
  }
});
