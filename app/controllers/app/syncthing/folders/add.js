import Ember from 'ember';
import handleModelError from '../../../../utils/handle-model-error';
import cardColor from '../../../../utils/card-color';


export default Ember.Controller.extend({
  breadCrumb: {name: 'New folder', icon: 'folder'},
  fields: {
    label: ['empty'],
    path: ['regExp[/^(/[^/ ]*)+/?$/]', 'empty'],
    keepVersions: ['integer', 'empty'],
    rescanIntervalS: ['integer', 'empty']
  },
  rescanIntervalS: 60,
  keepVersions: 3,
  cardColor: function() {
    return cardColor();
  }.property(),
  actions: {
    save: function() {
      var self = this,
          devices = this.get('devicesSelected').map(function(i) { return i.get('deviceID'); });
      var folder = self.store.createRecord('folder', {
        label: this.get('label'),
        path: this.get('path'),
        type: this.get('readOnly') ? "readonly" : "readwrite",
        ignorePerms: this.get('ignorePerms') || false,
        versioning: this.get('versioning') ? {type: "simple", params: {keep: this.get("keepVersions")}} : {type: "", params: {}},
        rescanIntervalS: this.get('rescanIntervalS'),
        devices: devices
      });
      var promise = folder.save();
      promise.then(function() {
        self.transitionToRoute('app.syncthing.folders');
      }, function(e){
        handleModelError(self, e);
        folder.deleteRecord();
      });
    },
    redirect: function() {
      this.transitionToRoute('app.syncthing.folders');
    }
  }
});
