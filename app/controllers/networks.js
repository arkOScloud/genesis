import Ember from "ember";


export default Ember.ObjectController.extend({
  actions: {
    toggle: function(net) {
      var self = this;
      net.set('operation', net.get('connected')?'disconnect':'connect');
      net.set('isReady', false);
      var promise = net.save();
      promise.then(function(){}, function(e){
        if (e.status == 500) self.transitionToRoute("error", e);
      });
    },
    toggleEnabled: function(net) {
      var self = this;
      net.set('operation', net.get('enabled')?'disable':'enable');
      net.set('isReady', false);
      var promise = net.save();
      promise.then(function(){}, function(e){
        if (e.status == 500) self.transitionToRoute("error", e);
      });
    }
  }
});
