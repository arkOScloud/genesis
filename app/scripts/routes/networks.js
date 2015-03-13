Genesis.NetworksRoute = Ember.Route.extend({
  model: function() {
    return Ember.RSVP.hash({
      networks: this.get('store').find('network'),
      netifaces: this.get('store').find('netiface')
    });
  },
  actions: {
    delete: function(model){
      model.destroyRecord().then(function(){}, function(){
        model.rollback();
      });
    }
  }
});
