import Ember from 'ember';

export default Ember.Controller.extend({
  breadCrumb: Ember.computed("model.id", {
    get() {
      return {name: this.get("model.id"), icon: 'sitemap'};
    }
  }),
  iface: function() {
    return this.get('netifaces').findBy('id', this.get('model.config').interface);
  }.property('netifaces'),
  address: function() {
    var addr = this.get('iface.up')?this.get('iface.ip')[0]:{addr: "None", netmask: "None"};
    return addr.addr+"/"+addr.netmask;
  }.property('iface'),
  actions: {
    openModal: function(name) {
      Ember.$('.ui.' + name + '.modal').modal('show');
    },
    deleteNet: function() {
      var self = this;
      Ember.$('.ui.delete-net.modal').modal('hide', function() {
        self.get('model').destroyRecord();
        self.transitionToRoute('settings.networks');
      });
      this.transitionToRoute('settings.networks');
    }
  }
});
