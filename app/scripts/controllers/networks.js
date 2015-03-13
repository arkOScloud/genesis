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

Genesis.NetworkAddController = Ember.ObjectController.extend({
  newConn: {config: {}},
  connTypes: [{id: "ethernet", name: "Ethernet"}, {id: "wireless", name: "Wireless"}],
  ipTypes: [{id: "dhcp", name: "Automatic (DHCP)"}, {id: "static", name: "Static"}],
  secTypes: [{id: "none", name: "None"}, {id: "wep", name: "WEP"}, {id: "wpa", name: "WPA (or WPA2)"}],
  isStatic: function() {
    return this.get('newConn').config.addressing == "static";
  }.property('newConn.config.addressing'),
  isWireless: function() {
    return !!this.get('newIface')?this.get('newIface').get('type')=="wireless":false;
  }.property('newIface.type'),
  isSecure: function() {
    return this.get('newConn').config.security != "none";
  }.property('newConn.config.security'),
  actions: {
    save: function() {
      var self   = this,
          config = this.get('newConn').config;
      config.connection = this.get('newIface').get('type');
      config.interface = this.get('newIface').get('id');
      var net = this.store.createRecord('network', {
        id: self.get('newConn').id,
        config: config,
        isReady: false
      });
      net.save();
    }
  }
});

Genesis.NetworkInfoController = Ember.ObjectController.extend({
  iface: function() {
    return this.get('model.extra.netifaces').findBy('id', this.get('model.config').interface);
  }.property('model.extra.netifaces'),
  address: function() {
    var addr = this.get('iface.up')?this.get('iface.ip')[0]:{addr: "None", netmask: "None"};
    return addr.addr+"/"+addr.netmask;
  }.property('iface')
});
