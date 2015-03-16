Genesis.BackupsRoute = Ember.Route.extend({
  model: function() {
    return Ember.RSVP.hash({
      backups: this.get('store').find('backup'),
      types: $.getJSON(Genesis.Config.krakenHost+'/backups/types').then(function(j){return j.types;})
    });
  },
  actions: {
    restore: function(model){
      model.set('isReady', false);
      model.save();
    },
    delete: function(model){
      model.destroyRecord().then(function(){}, function(){
        model.rollback();
      });
    }
  }
});
