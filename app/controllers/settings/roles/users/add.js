import Ember from 'ember';
import cardColor from '../../../../utils/card-color';


export default Ember.Controller.extend({
  breadCrumb: {name: 'New user', icon: 'fa-user'},
  newUser: {cardColor: cardColor()},
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
    }
  },
  actions: {
    save: function() {
      var self = this;
      var user = self.store.createRecord('user', {
        name: self.get('newUser').name,
        firstName: self.get('newUser').firstName,
        lastName: self.get('newUser').lastName,
        admin: self.get('newUser').admin || false,
        sudo: self.get('newUser').sudo || false,
        domain: self.get('newUser').domain,
        passwd: self.get('newUser').passwd,
        cardColor: self.get('newUser').cardColor
      });
      var promise = user.save();
      promise.then(function(){
        self.set('newUser', {cardColor: cardColor()});
        self.transitionToRoute("settings.roles.users");
      }, function(e){
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        }
        user.deleteRecord();
      });
    },
    redirect: function() {
      this.set('newUser', {cardColor: cardColor()});
      this.transitionToRoute('settings.roles.users');
    }
  }
});
