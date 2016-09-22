import Ember from 'ember';

export default Ember.Controller.extend({
  breadCrumb: Ember.computed("model.name", "model.icon", {
    get() {
      return {name: this.get("model.name"), icon: this.get("model.icon")};
    }
  }),
  actions: {
    openModal: function(name) {
      Ember.$('.ui.' + name + '.modal').modal('show');
    },
    uninstallApp: function() {
      var app = this.get('model'),
          self = this;
      app.set('operation', 'uninstall');
      app.set('isReady', false);
      app.save();
      Ember.$('.ui.uninstall-app.modal').modal('hide', function() {
        self.transitionToRoute('apps');
      });
    }
  }
});
