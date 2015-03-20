import Ember from "ember";


export default Ember.Route.extend({
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
