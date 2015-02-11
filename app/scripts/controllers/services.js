Genesis.ServicesController = Ember.ObjectController.extend({
  filterQuery: '',
  filteredServices: Ember.computed.filter('model', function(i) {
    return i.get('id').indexOf(this.get('filterQuery'))>=0;
  }).property('model', 'filterQuery'),
  actions: {
    clearFilter: function() {
      this.set('filterQuery', '');
    },
    toggleState: function(svc) {
      var op = svc.get('running')?'stop':'start';
      svc.set('isReady', false);
      svc.set('operation', op);
      var promise = svc.save();
      promise.then(function(){}, function(){
        this.get('model').rollback();
      });
    },
    toggleFileState: function(svc) {
      var op = svc.get('enabled')?'disable':'enable';
      svc.set('isReady', false);
      svc.set('operation', op);
      var promise = svc.save();
      promise.then(function(){}, function(){
        this.get('model').rollback();
      });
    }
  }
});
