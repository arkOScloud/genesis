Genesis.AppController = Ember.ObjectController.extend();

Genesis.AppsController = Ember.ObjectController.extend({
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
