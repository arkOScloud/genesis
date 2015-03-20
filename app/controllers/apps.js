import Ember from "ember";


export default Ember.ObjectController.extend({
  sortBy: ['name'],
  sortedApps: Ember.computed.sort('model', 'sortBy'),
  actions: {
    install: function(app) {
      app.set('operation', 'install');
      app.set('isReady', false);
      app.save();
    }
  }
});
