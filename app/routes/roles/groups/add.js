import Ember from 'ember';

export default Ember.Route.extend({
  renderTemplate: function() {
    this.render('roles.groups.add', { into: 'application' });
  },
  afterModel: function() {
    var me = this;
    var usersPromise = this.store.findAll('user');

    usersPromise.then(function(users) {
      me.controllerFor('roles.groups.add').set('users', users);
    });

    return usersPromise;
  }
});
