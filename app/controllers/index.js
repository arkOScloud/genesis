import Ember from "ember";


export default Ember.Controller.extend({
  sortBy: ['name'],
  sortedApps: Ember.computed.sort('model', 'sortBy'),
  filteredApps: Ember.computed.filterBy('sortedApps', 'displayInMenu', true),
  actions: {
    openApplication: function(app) {
      this.transitionToRoute(app.get('displayHref'));
    }
  }
});
