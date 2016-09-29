import Ember from "ember";
import handleModelError from '../../utils/handle-model-error';


export default Ember.ObjectController.extend({
  breadCrumb: {name: 'Services', icon: 'tasks'},
  queryParams: ['filter'],
  filter: null,
  filteredServices: Ember.computed.filter('model', function(i) {
    return this.get('filter') ? i.get('id').toLowerCase().indexOf(this.get('filter').toLowerCase()) >= 0 : true;
  }).property('model', 'filter'),
  actions: {
    clearFilter: function() {
      this.set('filter', null);
    },
    toggleState: function(svc) {
      var self = this;
      var op = svc.get('running')?'stop':'start';
      svc.set('isReady', false);
      svc.set('operation', op);
      var promise = svc.save();
      promise.then(function(){}, function(e){
        handleModelError(self, e);
        svc.rollback();
      });
    },
    toggleFileState: function(svc) {
      var self = this;
      var op = svc.get('enabled')?'disable':'enable';
      svc.set('isReady', false);
      svc.set('operation', op);
      var promise = svc.save();
      promise.then(function(){}, function(e){
        handleModelError(self, e);
        svc.rollback();
      });
    }
  }
});
