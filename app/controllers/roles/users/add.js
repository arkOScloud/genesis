import Ember from 'ember';

export default Ember.Controller.extend({
  breadCrumb: {name: 'New user', icon: 'fa-user'},
  newUser: {},
  actions: {
    save: function(){
      var self = this;
      var user = self.store.createRecord('user', {
        name: self.get('newUser').name,
        firstName: self.get('newUser').firstName,
        lastName: self.get('newUser').lastName,
        admin: self.get('newUser').admin || false,
        sudo: self.get('newUser').sudo || false,
        domain: self.get('newUser').domain,
        passwd: self.get('newUser').passwd
      });
      var promise = user.save();
      promise.then(function(){}, function(e){
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        }
        user.deleteRecord();
      });
    }
  }
});
