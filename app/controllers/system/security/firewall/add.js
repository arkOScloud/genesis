import Ember from 'ember';
import handleModelError from '../../../../utils/handle-model-error';
import cardColor from '../../../../utils/card-color';


export default Ember.Controller.extend({
  breadCrumb: {name: 'New firewall rule', icon: 'shield'},
  cardColor: function() {
    return cardColor();
  }.property(),
  policyList: [
    {id: "2", name: "Allow All Connections"},
    {id: "1", name: "Local Network Only"},
    {id: "0", name: "Deny All Connections"}
  ],
  fields: {
    identifier: ['regExp[/^[a-zA-Z0-9-]+$/]', 'empty'],
    name: ['empty'],
    tcp: ['regExp[/^(\\d+)*(,\\s*\\d+)*$/]'],
    udp: ['regExp[/^(\\d+)*(,\\s*\\d+)*$/]']
  },
  computedPorts: function() {
    var ports = [];
    var tcpPorts = (this.get('tcp') || '').replace(/ /g, '').split(','),
        udpPorts = (this.get('udp') || '').replace(/ /g, '').split(',');
    tcpPorts.forEach(function(p) {
      if (p) {
        ports.pushObject(['tcp', p]);
      }
    });
    udpPorts.forEach(function(p) {
      if (p) {
        ports.pushObject(['udp', p]);
      }
    });
    return ports;
  }.property('tcp', 'udp'),
  computedPortsString: function() {
    var ports = [];
    this.get("computedPorts").forEach(function(p) {
      ports.pushObject(`${p[1]} (${p[0]})`);
    });
    return ports.join(", ");
  }.property('computedPorts'),
  actions: {
    save: function() {
      var self = this;
      var policy = this.store.createRecord('policy', {
        id: this.get("identifier"),
        name: this.get("name"),
        ports: this.get("computedPorts"),
        policy: this.get("policy.id") || this.get("policyList.firstObject.id")

      });
      var promise = policy.save();
      promise.then(function() {
        self.transitionToRoute("system.security.firewall");
      }, function(e){
        handleModelError(self, e);
        policy.deleteRecord();
      });
    },
    redirect: function() {
      this.transitionToRoute('system.security.firewall');
    }
  }
});
