import Ember from 'ember';
import handleModelError from '../../../utils/handle-model-error';


export default Ember.Controller.extend({
  actions: {
    allow: function(policy) {
      var self = this;
      policy.set('policy', 2);
      policy.set('isReady', false);
      var promise = policy.save();
      promise.then(function(){}, function(e){
        handleModelError(self, e);
      });
    },
    local: function(policy) {
      var self = this;
      policy.set('policy', 1);
      policy.set('isReady', false);
      var promise = policy.save();
      promise.then(function(){}, function(e){
        handleModelError(self, e);
      });
    },
    deny: function(policy) {
      var self = this;
      policy.set('policy', 0);
      policy.set('isReady', false);
      var promise = policy.save();
      promise.then(function(){}, function(e){
        handleModelError(self, e);
      });
    },
    openModal: function(name, policy) {
      this.set('selectedPolicy', policy);
      Ember.$('.ui.' + name + '.modal').modal('show');
    },
    deletePolicy: function() {
      this.get('selectedPolicy').destroyRecord();
    }
  }
});
