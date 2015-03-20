import Ember from "ember";
import ENV from "../config/environment";
import toB64 from "../utils/to-b64";


export default Ember.Route.extend({
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
        var data = $.getJSON(ENV.APP.krakenHost+'/files/'+toB64("/"), function(j) {
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
          url: ENV.APP.krakenHost+'/files/'+toB64(i.path),
          type: "DELETE",
          success: function(){
            self.get('controller.currentFolder').removeObject(i);
          }
        })
      });
    }
  }
});
