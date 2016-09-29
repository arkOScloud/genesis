import Ember from 'ember';
import handleModelError from '../../../utils/handle-model-error';
import cardColor from '../../../utils/card-color';


export default Ember.Controller.extend({
  breadCrumb: {name: 'New network', icon: 'sitemap'},
  cardColor: cardColor(),
  ipTypes: [{id: "dhcp", name: "Automatic (DHCP)"}, {id: "static", name: "Static"}],
  secTypes: [{id: "none", name: "None"}, {id: "wep", name: "WEP"}, {id: "wpa", name: "WPA (or WPA2)"}],
  isStatic: function() {
    return this.get('addressing.id') === "static";
  }.property('addressing'),
  isWireless: function() {
    return !!this.get('netiface')?this.get('netiface.type') === "loopback":false;
  }.property('netiface'),
  isSecure: function() {
    return this.get('security.id') !== "none";
  }.property('security'),
  fields: {
    name: {
      rules: [
        {
          type: 'empty'
        },
        {
          type: 'maxLength[30]'
        }
      ]
    },
    address: {
      rules: [
        {
          type: 'regExp[/^([0-9]{1,3}\.){3}[0-9]{1,3}(\/([0-9]|[1-2][0-9]|3[0-2]))$/]',
          prompt: 'Address must be in IPv4 notation and have a CIDR number (192.168.0.1/24)'
        },
        {
          type: 'empty'
        }
      ]
    },
    gateway: {
      rules: [
        {
          type: 'regExp[/^([0-9]{1,3}\.){3}[0-9]{1,3}(\/([0-9]|[1-2][0-9]|3[0-2]))$/]',
          prompt: 'Address must be in IPv4 notation and have a CIDR number (192.168.0.1/24)'
        },
        {
          type: 'empty'
        }
      ]
    },
    essid: {
      rules: [
        {
          type: 'empty'
        }
      ]
    },
    passphrase: {
      rules: [
        {
          type: 'empty'
        }
      ]
    }
  },
  actions: {
    save: function() {
      var self = this;
      var netiface = this.get('netiface') || this.get('netifaces.firstObject');
      var config = {
        description: this.get('description'),
        connection: netiface.get('type'),
        interface: netiface.get('id')
      };
      if (this.get('isStatic')) {
        config.address = this.get('address');
        config.gateway = this.get('gateway');
      }
      if (this.get('isWireless')) {
        config.essid = this.get('essid');
        config.security = this.get('security').id;
        if (this.get('isSecure')) {
          config.key = this.get('key');
        }
      }
      var net = this.store.createRecord('network', {
        id: this.get('name'),
        config: config,
        isReady: false
      });
      var promise = net.save();
      promise.then(function(){
        self.setProperties({
          id: '', description: '', address: '', gateway: '', key: '',
          addressing: self.get('ipTypes.firstObject'),
          security: self.get('secTypes.firstObject'),
          netiface: self.get('netifaces.firstObject')
        });
        self.transitionToRoute("system.networks");
      }, function(e){
        handleModelError(self, e);
        net.deleteRecord();
      });
    },
    redirect: function() {
      this.setProperties({
        id: '', description: '', address: '', gateway: '', key: '',
        addressing: this.get('ipTypes.firstObject'),
        security: this.get('secTypes.firstObject'),
        netiface: this.get('netifaces.firstObject')
      });
      this.transitionToRoute('system.networks');
    }
  }
});
