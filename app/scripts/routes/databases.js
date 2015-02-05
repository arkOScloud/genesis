Genesis.DatabasesRoute = Ember.Route.extend({
  model: function() {
    return Ember.RSVP.hash({
      dbs: this.get('store').find('database'),
      users: this.get('store').find('databaseUser'),
      types: this.get('store').find('databaseType')
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
