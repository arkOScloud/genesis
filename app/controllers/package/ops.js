import Ember from "ember";
import ENV from "../../config/environment";


export default Ember.ObjectController.extend({
  sortBy: ['id'],
  rawOperations: function() {
    return this.get('model').filter(function(i) {
      return i.get('operation') !== "";
    });
  }.property('model.@each.operation'),
  pendingOperations: Ember.computed.sort('rawOperations', 'sortBy'),
  actions: {
    clear: function() {
      this.get('pendingOperations').forEach(function(i) {
        i.set('operation', '');
      });
    },
    save: function() {
      var self = this;
      var toSend = Ember.A();
      this.get('pendingOperations').forEach(function(i) {
        toSend.pushObject({id: i.get('id'), operation: i.get('operation')});
        i.set('operation', '');
      });
      Ember.$.ajax({
        url: ENV.APP.krakenHost+'/api/system/packages',
        data: JSON.stringify({packages: toSend}),
        type: 'POST',
        contentType: 'application/json',
        processData: false,
        error: function(e){
          if (e.status === 500) {
            self.transitionToRoute("error", e);
          }
        }
      });
    }
  }
});
