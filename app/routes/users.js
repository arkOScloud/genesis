import Ember from "ember";


export default Ember.Route.extend({
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
