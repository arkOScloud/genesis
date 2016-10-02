import Ember from 'ember';
import handleModelError from '../../../../utils/handle-model-error';
import cardColor from '../../../../utils/card-color';


export default Ember.Controller.extend({
  breadCrumb: {name: 'New share', icon: 'external share'},
  validUsers: Ember.A(),
  cardColor: function() {
    return cardColor();
  }.property(),
  fields: {
    name: ['empty'],
    path: ['regExp[/^(/[^/ ]*)+/?$/]', 'empty']
  },
  actions: {
    save: function(){
      var self = this;
      var share = this.store.createRecord('share', {
        id: this.get('name'),
        shareType: this.get('shareType') || this.get('model.shareTypes.firstObject'),
        path: this.get('path'),
        comment: this.get('comment') || "",
        validUsers: this.get('validUsers'),
        readOnly: this.get('readOnly') || false,
        isReady: false
      });
      var promise = share.save();
      promise.then(function(){
        self.transitionToRoute("tools.shares.shares");
      }, function(e){
        handleModelError(self, e);
        share.deleteRecord();
      });
    },
    redirect: function() {
      this.transitionToRoute('tools.shares.shares');
    }
  }
});
