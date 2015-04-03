import Ember from "ember";


export default Ember.ObjectController.extend({
  sortBy: ['name'],
  sortedApps: Ember.computed.sort('model', 'sortBy'),
  actions: {
    install: function(app) {
      var self = this;
      app.set('operation', 'install');
      app.set('isReady', false);
      var promise = app.save();
      promise.then(function(){}, function(e){
        if (e.status == 500) self.transitionToRoute("error", e);
      });
    }
  }
});
