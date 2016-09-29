import Ember from 'ember';
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  renderTemplate: function() {
    this.render('system.roles.users.edit', { into: 'application' });
  },
  afterModel: function() {
    var me = this;
    var domainsPromise = this.store.findAll('domain');

    domainsPromise.then(function(domains) {
      me.controllerFor('system.roles.users.edit').set('domains', domains);
    });

    return domainsPromise;
  }
});
