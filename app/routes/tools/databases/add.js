import Ember from 'ember';
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  renderTemplate: function() {
    this.render('tools.databases.add', { into: 'application' });
  },
  afterModel: function() {
    var me = this;
    var dbPromise = this.store.findAll('database-type');

    dbPromise.then(function(dbTypes) {
      me.controllerFor('tools.databases.add').set('dbTypes', dbTypes);
    });

    return dbPromise;
  }
});
