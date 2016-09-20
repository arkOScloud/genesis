import Ember from 'ember';

export default Ember.Controller.extend({
  breadCrumb: {name: 'Users, Groups and Domains', icon: 'fa-group'},
  selectedGroup: null,
  actions: {
    openModal: function(name, group) {
      this.set('selectedGroup', group);
      Ember.$('.ui.' + name + '.modal').modal('show');
    },
    deleteGroup: function() {
      this.get('selectedGroup').deleteRecord();
      this.set('selectedGroup', null);
    },
    clearModal: function() {
      this.set('selectedGroup', null);
    }
  }
});
