import Ember from 'ember';

export default Ember.Route.extend({
  renderTemplate: function() {
    this.render('roles.groups.edit', { into: 'application' });
  },
  afterModel: function() {
    var me = this;
    var usersPromise = this.store.findAll('user');

    usersPromise.then(function(users) {
      me.controllerFor('roles.groups.edit').set('users', users);
    });

    return usersPromise;
  }
});
