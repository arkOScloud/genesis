import Ember from "ember";


export default Ember.ObjectController.extend({
  sortBy: ['id'],
  sortedSites: Ember.computed.sort('model.sites', 'sortBy'),
  actions: {
    toggleStatus: function(site) {
      site.set('operation', site.get('enabled')?'disable':'enable');
      site.save();
    }
  }
});
