import Ember from 'ember';
import handleModelError from '../../../utils/handle-model-error';
import cardColor from '../../../utils/card-color';


export default Ember.Controller.extend({
  breadCrumb: {name: 'New database user', icon: 'user'},
  cardColor: cardColor(),
  userTypes: function(){
    return this.get('types').filterProperty('supportsUsers', true);
  }.property('types'),
  fields: {
    username: {
      rules: [
        {
          type: 'empty'
        },
        {
          type: 'regExp[/^[a-zA-Z][a-zA-Z0-9-_]{1,80}$/]',
          prompt: '{name} must be letters or numbers, must start with a letter, and less than 80 characters'
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
    save: function(){
      var self = this;
      var db = this.store.createRecord('databaseUser', {
        id: this.get('id'),
        databaseType: this.get('dbType') || this.get('userTypes.firstObject'),
        passwd: this.get('passwd')
      });
      var promise = db.save();
      promise.then(function(){
        self.setProperties({
          id: '', passwd: '', passwdb: '', dbType: self.get('userTypes.firstObject')
        });
        self.transitionToRoute("tools.databases");
      }, function(e){
        handleModelError(self, e);
        db.deleteRecord();
      });
    },
    redirect: function() {
      this.setProperties({
        id: '', passwd: '', passwdb: '', dbType: this.get('userTypes.firstObject')
      });
      this.transitionToRoute('tools.databases');
    }
  }
});
