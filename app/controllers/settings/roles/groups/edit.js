import Ember from 'ember';
import handleModelError from '../../../../utils/handle-model-error';


export default Ember.Controller.extend({
  breadCrumb: Ember.computed("model.name", {
    get() {
      return {name: this.get("model.name"), icon: 'group'};
    }
  }),
  actions: {
    save: function(){
      var self = this;
      var group = this.get('model');
      group.set('isReady', false);
      var promise = group.save();
      promise.then(function(){
        self.transitionToRoute("settings.roles.groups");
      }, function(e){
        handleModelError(self, e);
      });
    },
    redirect: function() {
      this.get('model').rollback();
      this.transitionToRoute('settings.roles.groups');
    },
    openModal: function(name) {
      Ember.$('.ui.' + name + '.modal').modal('show');
    },
    deleteGroup: function() {
      var self = this;
      this.get('model').destroyRecord();
      Ember.$('.ui.delete-group.modal').modal('hide', function() {
        self.transitionToRoute('settings.roles.groups');
      });
    }
  }
});
