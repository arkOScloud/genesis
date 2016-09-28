import Ember from 'ember';
import handleModelError from '../../../utils/handle-model-error';


export default Ember.Controller.extend({
  breadCrumb: Ember.computed("model.id", {
    get() {
      return {name: this.get("model.id"), icon: 'certificate'};
    }
  }),
  actions: {
    save: function(){
      var self    = this,
          cert    = this.get('model');
      cert.set('isReady', false);
      var promise = cert.save();
      promise.then(function(){
        this.transitionToRoute('tools.certificates');
      }, function(e){
        handleModelError(self, e);
      });
    },
    redirect: function() {
      this.get('model').rollback();
      this.transitionToRoute('tools.certificates');
    },
    openModal: function(name) {
      Ember.$('.ui.' + name + '.modal').modal('show');
    },
    deleteCert: function() {
      var self = this;
      this.get('model').destroyRecord();
      Ember.$('.ui.delete-cert.modal').modal('hide', function() {
        self.transitionToRoute('tools.certificates');
      });
    }
  }
});
