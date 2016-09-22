import Ember from 'ember';
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  renderTemplate: function() {
    this.render('settings.roles.groups.add', { into: 'application' });
  },
  afterModel: function() {
    var me = this;
    var usersPromise = this.store.findAll('user');

    usersPromise.then(function(users) {
      me.controllerFor('settings.roles.groups.add').set('users', users);
    });

    return usersPromise;
  }
});
