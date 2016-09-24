import Ember from 'ember';
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  renderTemplate: function() {
    this.render('websites.add', { into: 'application' });
  },
  afterModel: function() {
    var me = this;
    var usersPromise = this.store.findAll('user');
    var typesPromise = this.store.query('app', {installed: true, type: 'website'});
    var dbmanPromise = this.store.findAll('database-type');
    var domainsPromise = this.store.findAll('domain');

    usersPromise.then(function(users) {
      me.controllerFor('websites.add').set('users', users);
    });

    typesPromise.then(function(types) {
      me.controllerFor('websites.add').set('siteTypes', types);
    });

    dbmanPromise.then(function(dbtypes) {
      me.controllerFor('websites.add').set('dbtypes', dbtypes);
    });

    domainsPromise.then(function(domains) {
      me.controllerFor('websites.add').set('domains', domains);
    });

    return domainsPromise;
  }
});
