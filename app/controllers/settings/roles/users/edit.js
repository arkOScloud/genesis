import Ember from 'ember';
import handleModelError from '../../../../utils/handle-model-error';


export default Ember.Controller.extend({
  breadCrumb: Ember.computed("model.name", {
    get() {
      return {name: this.get("model.name"), icon: 'user'};
    }
  }),
  fields: {
    firstName: {
      rules: [
        {
          type: 'regExp[/^[a-zA-Z][a-zA-Z0-9_-]*$/]'
        },
        {
          type: 'empty'
        }
      ]
    },
    password: {
      optional: true,
      rules: [
        {
          type: 'minLength[6]'
        }
      ]
    },
    passwordConf: {
      rules: [
        {
          type: 'match[password]'
        }
      ]
    }
  },
  actions: {
    save: function(){
      var self = this;
      var user = this.get('model');
      user.set('isReady', false);
      var promise = user.save();
      promise.then(function(){
        self.transitionToRoute("settings.roles.users");
      }, function(e){
        handleModelError(self, e);
      });
    },
    redirect: function() {
      this.get('model').rollback();
      this.transitionToRoute('settings.roles.users');
    },
    openModal: function(name) {
      Ember.$('.ui.' + name + '.modal').modal('show');
    },
    deleteUser: function() {
      var self = this;
      Ember.$('.ui.delete-user.modal').modal('hide', function() {
        self.get('model').destroyRecord();
        self.transitionToRoute('settings.roles.users');
      });
    }
  }
});
