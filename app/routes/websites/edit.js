import Ember from 'ember';
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  renderTemplate: function() {
    this.render('websites.edit', { into: 'application' });
  },
  afterModel: function() {
    var me = this;
    var domainsPromise = this.store.findAll('domain');

    domainsPromise.then(function(domains) {
      me.controllerFor('websites.edit').set('domains', domains);
    });

    return domainsPromise;
  }
});
