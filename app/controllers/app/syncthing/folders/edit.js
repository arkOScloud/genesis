import Ember from 'ember';
import handleModelError from '../../../../utils/handle-model-error';


export default Ember.Controller.extend({
  breadCrumb: Ember.computed("model.label", {
    get() {
      return {name: this.get("model.label"), icon: 'folder'};
    }
  }),
  fields: {
    name: ['empty'],
    path: ['regExp[/^(/[^/ ]*)+/?$/]', 'empty'],
    keepVersions: ['integer', 'empty'],
    rescanIntervalS: ['integer', 'empty']
  },
  readOnly: function() {
    return this.get('model.isReadOnly');
  }.property('model'),
  devicesSelected: function() {
    var data = [],
        ids = this.get('model.devices').map(function(i) { return i.deviceID; });
    this.get('devicesAvailable').forEach(function(i) {
      if (ids.indexOf(i.deviceID) !== -1) {
        data.pushObject(i);
      }
    });
    return data;
  }.property('devicesAvailable', 'model.devices'),
  devicesAvailable: function() {
    var data = [];
    if (this.get('devices')) {
      return this.get('devices').map(function(i) {
        return {name: i.get('name'), deviceID: i.get('deviceID')};
      });
    }
    return data;
  }.property('devices'),
  actions: {
    save: function() {
      var self = this,
          folder = this.get("model");
      folder.set("type", folder.get("isReadOnly") ? "readonly" : "readwrite");
      folder.set("versioning",
        folder.get("hasVersioning") ? {type: "simple", params: {keep: folder.get("versioning.params.keep") || 3}} : {type: "", params: {}}
      );
      folder.set("devices", this.get("devicesSelected"));
      var promise = folder.save();
      promise.then(function(){
        self.transitionToRoute("app.syncthing.folders");
      }, function(e){
        handleModelError(self, e);
      });
    },
    redirect: function() {
      this.get('model').rollback();
      this.transitionToRoute('app.syncthing.folders');
    },
    openModal: function(name) {
      Ember.$('.ui.' + name + '.modal').modal('show');
    },
    deleteFolder: function() {
      var self = this;
      Ember.$('.ui.delete-folder.modal').modal('hide', function() {
        self.get('model').destroyRecord();
        self.transitionToRoute('app.syncthing.folders');
      });
    }
  }
});
