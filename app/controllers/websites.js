import Ember from "ember";
import handleModelError from '../utils/handle-model-error';
import ENV from "../config/environment";


export default Ember.ObjectController.extend({
  breadCrumb: {name: 'Websites', icon: 'globe'},
  queryParams: ['filter'],
  filter: null,
  sortBy: ['id'],

  sortedSites: Ember.computed.sort('model', 'sortBy'),
  filteredSites: Ember.computed.filter('sortedSites', function(site) {
    if (this.get('filter')) {
      return (site.get('id').toLowerCase().indexOf(this.get('filter').toLowerCase()) >= 0 ||
              site.get('appName').toLowerCase().indexOf(this.get('filter').toLowerCase()) >= 0);
    }
    return true;
  }).property('filter', 'sortedSites'),

  actions: {
    toggleStatus: function(site) {
      var self = this;
      site.set('operation', site.get('enabled') ? 'disable' : 'enable');
      var promise = site.save();
      promise.then(function(){}, function(e){
        handleModelError(self, e);
      });
    },
    clearFilter: function() {
      this.set('filter', null);
    },
    openModal: function(name, site) {
      this.set('selectedSite', site);
      Ember.$('.ui.' + name + '.modal').modal('show');
    },
    deleteSite: function(){
      var site = this.get('selectedSite');
      site.set('isReady', false);
      Ember.$.ajax(`${ENV.APP.krakenHost}/api/websites/${site.get('id')}`, {type: 'DELETE'});
      this.set('selectedSite', null);
    }
  }
});
