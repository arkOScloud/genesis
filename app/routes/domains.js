import Ember from "ember";


export default Ember.Route.extend({
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
