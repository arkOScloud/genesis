import Ember from 'ember';

export default Ember.Controller.extend({
  breadCrumb: Ember.computed("model.name", {
    get() {
      return {name: this.get("model.name"), icon: 'fa-group'};
    }
  }),
  actions: {
    save: function(){
      var self = this;
      var group = this.get('model');
      group.set('isReady', false);
      var promise = group.save();
      promise.then(function(){}, function(e){
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        }
      });
    },
    openModal: function(name) {
      Ember.$('.ui.' + name + '.modal').modal('show');
    },
    deleteGroup: function() {
      var self = this;
      this.get('model').destroyRecord();
      Ember.$('.ui.delete-group.modal').modal('hide', function() {
        self.transitionToRoute('roles.groups');
      });
    }
  }
});
