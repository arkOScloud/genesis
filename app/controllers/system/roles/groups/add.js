import Ember from 'ember';
import handleModelError from '../../../../utils/handle-model-error';
import cardColor from '../../../../utils/card-color';


export default Ember.Controller.extend({
  breadCrumb: {name: 'New group', icon: 'group'},
  newGroup: {cardColor: cardColor()},
  fields: {
    name: ['minLength[4]', 'empty']
  },
  actions: {
    save: function() {
      var self = this;
      var group = self.store.createRecord('group', {
        name: self.get('newGroup').name,
        users: self.get('newGroup').users,
        cardColor: self.get('newGroup').cardColor
      });
      var promise = group.save();
      promise.then(function() {
        self.set('newGroup', {cardColor: cardColor()});
        self.transitionToRoute("system.roles.groups");
      }, function(e){
        handleModelError(self, e);
        group.deleteRecord();
      });
    },
    redirect: function() {
      this.set('newGroup', {cardColor: cardColor()});
      this.transitionToRoute('system.roles.groups');
    }
  }
});
