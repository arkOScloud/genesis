import Ember from "ember";


export default Ember.ObjectController.extend({
  actions: {
    allow: function(policy) {
      policy.set('policy', 2);
      policy.set('isReady', false);
      policy.save();
      this.message.success('Policy changed successfully');
    },
    local: function(policy) {
      policy.set('policy', 1);
      policy.set('isReady', false);
      policy.save();
      this.message.success('Policy changed successfully');
    },
    deny: function(policy) {
      policy.set('policy', 0);
      policy.set('isReady', false);
      policy.save();
      this.message.success('Policy changed successfully');
    }
  }
});
