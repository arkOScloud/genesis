import Ember from "ember";


export default Ember.ObjectController.extend({
  breadCrumb: {name: 'Services', icon: 'fa-spinner'},
  queryParams: ['filter'],
  filter: null,
  filteredServices: Ember.computed.filter('model', function(i) {
    return this.get('filter') ? i.get('id').indexOf(this.get('filter')) >= 0 : true;
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
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        }
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
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        }
        svc.rollback();
      });
    }
  }
});
