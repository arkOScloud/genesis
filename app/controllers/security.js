import Ember from "ember";


export default Ember.ObjectController.extend({
  actions: {
    allow: function(policy) {
      var self = this;
      policy.set('policy', 2);
      policy.set('isReady', false);
      var promise = policy.save();
      promise.then(function(){
        self.message.success('Policy changed successfully');
      }, function(e){
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        }
      });
    },
    local: function(policy) {
      var self = this;
      policy.set('policy', 1);
      policy.set('isReady', false);
      var promise = policy.save();
      promise.then(function(){
        self.message.success('Policy changed successfully');
      }, function(e){
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        }
      });
    },
    deny: function(policy) {
      var self = this;
      policy.set('policy', 0);
      policy.set('isReady', false);
      var promise = policy.save();
      promise.then(function(){
        self.message.success('Policy changed successfully');
      }, function(e){
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        }
      });
    }
  }
});
