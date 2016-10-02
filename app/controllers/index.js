import Ember from "ember";


export default Ember.Controller.extend({
  sortBy: ['name'],
  sortedApps: Ember.computed.sort('model', 'sortBy'),
  filteredApps: Ember.computed.filterBy('sortedApps', 'displayInMenu', true),
  actions: {
    openApplication: function(app) {
      if (app.get('type') === 'website') {
        this.transitionToRoute('websites', {
          queryParams: {filter: app.get('name')}
        });
      } else if (app.get('type') === 'fileshare') {
        this.transitionToRoute('tools.shares.shares');
      } else {
        this.transitionToRoute(app.get('id'));
      }
    }
  }
});
