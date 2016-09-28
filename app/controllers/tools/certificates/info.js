import Ember from 'ember';

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
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        } else if (e.errors) {
          e.errors.forEach(function(err) {
            self.notifications.new('error', err.detail);
          });
        }
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
