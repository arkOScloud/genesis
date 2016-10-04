import Ember from 'ember';
import handleModelError from '../../../../utils/handle-model-error';


export default Ember.Controller.extend({
  breadCrumb: Ember.computed("model.name", {
    get() {
      return {name: this.get("model.name"), icon: 'disk outline'};
    }
  }),
  fields: {
    name: ['empty'],
    addresses: ['empty']
  },
  actions: {
    save: function() {
      var self = this,
          device = this.get("model");
      var promise = device.save();
      promise.then(function(){
        self.transitionToRoute("app.syncthing.devices");
      }, function(e){
        handleModelError(self, e);
      });
    },
    redirect: function() {
      this.get('model').rollback();
      this.transitionToRoute('app.syncthing.devices');
    },
    openModal: function(name) {
      Ember.$('.ui.' + name + '.modal').modal('show');
    },
    deleteDevice: function() {
      var self = this;
      Ember.$('.ui.delete-device.modal').modal('hide', function() {
        self.get('model').destroyRecord();
        self.transitionToRoute('app.syncthing.devices');
      });
    }
  }
});
