import Ember from "ember";


export default Ember.ObjectController.extend({
  actions: {
    save: function(){
      var self = this;
      var user = this.get('model');
      user.set('isReady', false);
      var promise = user.save();
      promise.then(function(){}, function(e){
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        }
      });
    },
    removeModal: function(){
      var user = this.get('model');
      user.setProperties({
        "passwd": "",
        "passwdb": ""
      });
      return true;
    }
  }
});
