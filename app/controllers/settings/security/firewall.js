import Ember from 'ember';

export default Ember.Controller.extend({
  actions: {
    allow: function(policy) {
      var self = this;
      policy.set('policy', 2);
      policy.set('isReady', false);
      var promise = policy.save();
      promise.then(function(){}, function(e){
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        } else if (e.errors) {
          e.errors.forEach(function(err) {
            self.notifications.new('error', err.detail);
          });
        }
      });
    },
    local: function(policy) {
      var self = this;
      policy.set('policy', 1);
      policy.set('isReady', false);
      var promise = policy.save();
      promise.then(function(){}, function(e){
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        } else if (e.errors) {
          e.errors.forEach(function(err) {
            self.notifications.new('error', err.detail);
          });
        }
      });
    },
    deny: function(policy) {
      var self = this;
      policy.set('policy', 0);
      policy.set('isReady', false);
      var promise = policy.save();
      promise.then(function(){}, function(e){
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        } else if (e.errors) {
          e.errors.forEach(function(err) {
            self.notifications.new('error', err.detail);
          });
        }
      });
    }
  }
});
