import Ember from 'ember';
import handleModelError from '../../../../utils/handle-model-error';
import cardColor from '../../../../utils/card-color';


export default Ember.Controller.extend({
  breadCrumb: {name: 'New mount', icon: 'folder'},
  cardColor: function() {
    return cardColor();
  }.property(),
  fields: {
    name: ['empty'],
    path: ['regExp[/^(/[^/ ]*)+/?$/]', 'empty'],
    networkPath: ['empty']
  },
  validShareTypes: Ember.computed.filterBy('model', 'supportsMounts', true),
  actions: {
    save: function(){
      var self = this;
      var mount = this.store.createRecord('mount', {
        shareType: this.get('shareType') || this.get('validShareTypes.firstObject'),
        path: this.get('path'),
        networkPath: this.get('networkPath'),
        readOnly: this.get('readOnly') || false,
        username: this.get('username'),
        password: this.get('password'),
        isReady: false
      });
      var promise = mount.save();
      promise.then(function(){
        self.transitionToRoute("tools.shares.mounts");
      }, function(e){
        handleModelError(self, e);
        mount.deleteRecord();
      });
    },
    redirect: function() {
      this.transitionToRoute('tools.shares.mounts');
    }
  }
});
