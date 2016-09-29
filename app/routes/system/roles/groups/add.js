import Ember from 'ember';
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  renderTemplate: function() {
    this.render('system.roles.groups.add', { into: 'application' });
  },
  afterModel: function() {
    var me = this;
    var usersPromise = this.store.findAll('user');

    usersPromise.then(function(users) {
      me.controllerFor('system.roles.groups.add').set('users', users);
    });

    return usersPromise;
  }
});
