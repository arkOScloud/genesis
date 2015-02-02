Genesis.UsersRoute = Ember.Route.extend({
  model: function() {
    return Ember.RSVP.hash({
      users: this.get('store').find('user'),
      domains: this.get('store').find('domain')
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

Genesis.GroupsRoute = Ember.Route.extend({
  model: function() {
    return Ember.RSVP.hash({
      groups: this.get('store').find('group'),
      users: this.get('store').find('user')
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

Genesis.DomainsRoute = Ember.Route.extend({
  model: function() {
    return this.get('store').find('domain');
  },
  actions: {
    delete: function(model){
      model.destroyRecord().then(function(){}, function(){
        model.rollback();
      });
    }
  }
});
