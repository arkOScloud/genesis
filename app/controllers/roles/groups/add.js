import Ember from 'ember';
import cardColor from '../../../utils/card-color';


export default Ember.Controller.extend({
  breadCrumb: {name: 'New group', icon: 'fa-group'},
  newGroup: {cardColor: cardColor()},
  actions: {
    save: function(){
      var self = this;
      var group = self.store.createRecord('group', {
        name: self.get('newGroup').name,
        users: self.get('newGroup').users,
        cardColor: self.get('newGroup').cardColor
      });
      var promise = group.save();
      promise.then(function(){}, function(e){
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        }
        group.deleteRecord();
      });
    }
  }
});
