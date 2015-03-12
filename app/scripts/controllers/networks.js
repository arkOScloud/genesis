Genesis.NetworkController = Ember.ObjectController.extend();

Genesis.NetworksController = Ember.ObjectController.extend({
  actions: {
    toggle: function(net) {
      net.set('operation', net.get('connected')?'disconnect':'connect');
      net.set('isReady', false);
      net.save();
    },
    toggleEnabled: function(net) {
      net.set('operation', net.get('enabled')?'disable':'enable');
      net.set('isReady', false);
      net.save();
    }
  }
});
