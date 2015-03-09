Genesis.AppsRoute = Ember.Route.extend({
  model: function() {
    return this.get('store').find('app');
  },
  actions: {
    delete: function(model){
      model.destroyRecord().then(function(){}, function(){
        model.rollback();
      });
    }
  }
});
