import Ember from "ember";


export default Ember.Controller.extend({
  sortBy: ['name'],
  sortedApps: Ember.computed.sort('model', 'sortBy'),
  actions: {
    openApplication: function(app) {
      this.transitionToRoute(app.get('displayHref'));
    }
  }
});
