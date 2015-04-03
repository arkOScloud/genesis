import Ember from "ember";


export default Ember.ObjectController.extend({
  sortBy: ['id'],
  sortedSites: Ember.computed.sort('model.sites', 'sortBy'),
  actions: {
    toggleStatus: function(site) {
      var self = this;
      site.set('operation', site.get('enabled')?'disable':'enable');
      var promise = site.save();
      promise.then(function(){}, function(e){
        if (e.status == 500) self.transitionToRoute("error", e);
      });
    }
  }
});
