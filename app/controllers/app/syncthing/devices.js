import Ember from 'ember';

export default Ember.Controller.extend({
  breadCrumb: {name: 'File Sync', icon: 'refresh'},
  actions: {
    openModal: function(name, device) {
      this.set('selectedDevice', device);
      Ember.$('.ui.' + name + '.modal').modal('show');
    },
    deleteDevice: function() {
      var self = this;
      Ember.$('.ui.delete-device.modal').modal('hide', function() {
        self.get('selectedDevice').destroyRecord();
        self.transitionToRoute('app.syncthing.devices');
      });
    }
  }
});
