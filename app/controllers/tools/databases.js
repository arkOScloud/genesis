import Ember from 'ember';

export default Ember.Controller.extend({
  breadCrumb: {name: 'Databases', icon: 'fa-database'},
  queryParams: ['filter'],
  filter: null,

  databasesFilter: function() {
    return this.get('filter') === null;
  }.property('filter'),
  usersFilter: function() {
    return this.get('filter') === 'users';
  }.property('filter'),

  actions: {
    setFilter: function(filter) {
      if (filter === 'users') {
        this.set('filter', 'users');
      } else {
        this.set('filter', null);
      }
    },
    openModal: function(name, db) {
      this.set('selectedDb', db);
      this.set('selectedUser', db);
      Ember.$('.ui.' + name + '.modal').modal('show');
    },
    deleteDb: function() {
      this.get('selectedDb').destroyRecord();
      this.set('selectedDb', null);
      this.set('selectedUser', null);
    },
    deleteUser: function() {
      this.get('selectedUser').destroyRecord();
      this.set('selectedDb', null);
      this.set('selectedUser', null);
    },
    clearModal: function() {
      this.set('selectedDb', null);
      this.set('selectedUser', null);
    }
  }
});
