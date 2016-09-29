import Ember from 'ember';

export default Ember.Controller.extend({
  breadCrumb: {name: 'Users, Groups and Domains', icon: 'group'},
  selectedUser: null,
  actions: {
    openModal: function(name, user) {
      this.set('selectedUser', user);
      Ember.$('.ui.' + name + '.modal').modal('show');
    },
    deleteUser: function() {
      this.get('selectedUser').destroyRecord();
      this.set('selectedUser', null);
    },
    clearModal: function() {
      this.set('selectedUser', null);
    }
  }
});
