Genesis.NetworksRoute = Ember.Route.extend({
  model: function() {
    return this.get('store').find('network');
  },
  actions: {
    delete: function(model){
      model.destroyRecord().then(function(){}, function(){
        model.rollback();
      });
    }
  }
});
