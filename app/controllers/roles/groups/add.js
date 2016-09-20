import Ember from 'ember';

export default Ember.Controller.extend({
  breadCrumb: {name: 'New group', icon: 'fa-group'},
  newGroup: {},
  actions: {
    save: function(){
      var self = this;
      var group = self.store.createRecord('group', {
        name: self.get('newGroup').name,
        users: self.get('newGroup').users
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
