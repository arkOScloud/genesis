import Ember from 'ember';
import handleModelError from '../../../../utils/handle-model-error';
import cardColor from '../../../../utils/card-color';


export default Ember.Controller.extend({
  breadCrumb: {name: 'New device', icon: 'disk outline'},
  fields: {
    name: ['empty'],
    deviceID: ['empty'],
    addresses: ['empty']
  },
  cardColor: function() {
    return cardColor();
  }.property(),
  actions: {
    save: function() {
      var self = this;
      var device = self.store.createRecord('device', {
        id: this.get('id'),
        name: this.get('id'),
        deviceID: this.get('deviceID'),
        addressing: this.get('addressing')
      });
      var promise = device.save();
      promise.then(function() {
        self.transitionToRoute('app.syncthing.devices');
      }, function(e){
        handleModelError(self, e);
        device.deleteRecord();
      });
    },
    redirect: function() {
      this.transitionToRoute('app.syncthing.devices');
    }
  }
});
