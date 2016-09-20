import Ember from 'ember';

export default Ember.Route.extend({
  renderTemplate: function() {
    this.render('roles.users.edit', { into: 'application' });
  },
  afterModel: function() {
    var me = this;
    var domainsPromise = this.store.findAll('domain');

    domainsPromise.then(function(domains) {
      me.controllerFor('roles.users.edit').set('domains', domains);
    });

    return domainsPromise;
  }
});
