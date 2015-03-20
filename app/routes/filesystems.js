import Ember from "ember";


export default Ember.Route.extend({
  beforeModel: function(model) {
    this.get('store').unloadAll('filesystem');
  },
  model: function() {
    return this.get('store').find('filesystem');
  },
  actions: {
    delete: function(model){
      model.destroyRecord().then(function(){}, function(){
        model.rollback();
      });
    }
  }
});
