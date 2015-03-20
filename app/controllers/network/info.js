import Ember from "ember";


export default Ember.ObjectController.extend({
  iface: function() {
    return this.get('model.extra.netifaces').findBy('id', this.get('model.config').interface);
  }.property('model.extra.netifaces'),
  address: function() {
    var addr = this.get('iface.up')?this.get('iface.ip')[0]:{addr: "None", netmask: "None"};
    return addr.addr+"/"+addr.netmask;
  }.property('iface')
});
