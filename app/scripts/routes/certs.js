Genesis.CertsRoute = Ember.Route.extend({
  model: function() {
    return Ember.RSVP.hash({
      certs: this.get('store').find('cert'),
      auths: this.get('store').find('certauth')
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
