import Ember from 'ember';

export default Ember.Controller.extend({
  breadCrumb: Ember.computed("model.id", {
    get() {
      return {name: this.get("model.id"), icon: 'external share'};
    }
  }),
  actions: {
    openModal: function(name) {
      Ember.$('.ui.' + name + '.modal').modal('show');
    },
    deleteShare: function() {
      var self = this;
      Ember.$('.ui.delete-share.modal').modal('hide', function() {
        self.get('model').destroyRecord();
        self.transitionToRoute('tools.shares.shares');
      });
    }
  }
});
