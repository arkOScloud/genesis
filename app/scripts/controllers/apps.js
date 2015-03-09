Genesis.AppController = Ember.ObjectController.extend();

Genesis.AppsController = Ember.ObjectController.extend({
  sortBy: ['name'],
  sortedApps: Ember.computed.sort('model', 'sortBy')
});
