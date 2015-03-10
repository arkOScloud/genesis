Genesis.IndexController = Ember.Controller.extend({
  sortBy: ['name'],
  sortedApps: Ember.computed.sort('model', 'sortBy')
});
