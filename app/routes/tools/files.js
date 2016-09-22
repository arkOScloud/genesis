import Ember from "ember";
import ENV from "../../config/environment";
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  model: function() {
    return Ember.RSVP.hash({
      shares: this.get('store').findAll('share'),
      POIs: this.get('store').findAll('point')
    });
  },
  setupController: function(controller, model) {
    this._super();
    controller.set('model', model);
    if (!this.get("currentPath")) {
        this.set('currentPath', "/");
        Ember.$.getJSON(ENV.APP.krakenHost+'/api/files/Lw**', function(j) {
          controller.set('currentFolder', j.files);
        });
    }
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
        Ember.$.ajax({
          url: ENV.APP.krakenHost+'/api/files/'+i.id,
          type: "DELETE",
          success: function(){
            self.get('controller.currentFolder').removeObject(i);
          }
        });
      });
    }
  }
});
