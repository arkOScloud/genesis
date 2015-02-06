Genesis.DatabasesRoute = Ember.Route.extend({
  afterModel: function(model) {
    var self = this;
    model.types.forEach(function(i) {
      if (!i.get('state')) self.message.danger(i.get('name')+' is not running. Start it via the Status button to see its databases and perform tasks.')
    });
  },
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
