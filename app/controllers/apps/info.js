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
      this.get('model').deleteRecord();
    }
  }
});
