import Ember from 'ember';
import handleModelError from '../../utils/handle-model-error';


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
    install: function() {
      var app = this.get('model'),
          self = this;
      app.set('operation', 'install');
      app.set('isReady', false);
      var promise = app.save();
      promise.then(function(){}, function(e){
        handleModelError(self, e);
      });
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
