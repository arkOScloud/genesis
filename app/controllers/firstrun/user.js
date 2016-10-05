import Ember from 'ember';

export default Ember.Controller.extend({
  newUser: {},
  newDomain: "arkos.local",
  fields: {
    username: {
      rules: [
        {
          type: 'empty'
        },
        {
          type: 'regExp[/^[a-z0-9]{2,30}$/]',
          prompt: '{name} must be lowercase letters or numbers, and less than 30 characters'
        }
      ]
    },
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
      rules: [
        {
          type: 'minLength[6]'
        },
        {
          type: 'empty'
        }
      ]
    },
    passwordConf: {
      rules: [
        {
          type: 'match[password]'
        }
      ]
    },
    domain: {
      rules: [
        {
          type: 'regExp[/^[a-zA-Z0-9-_\.]+$/]'
        }
      ]
    }
  },
  actions: {
    nextStep: function() {
      var self = this;
      Ember.$('#user-form').form({
        fields: this.get('fields'),
        keyboardShortcuts: false,
        onSuccess: function() {
          self.transitionToRoute("firstrun.settings");
        }
      });
      Ember.$('#user-form').form('validate form');
    }
  }
});
