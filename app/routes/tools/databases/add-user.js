import Ember from 'ember';
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  renderTemplate: function() {
    this.render('tools.databases.add-user', { into: 'application' });
  },
  afterModel: function() {
    var me = this;
    var dbPromise = this.store.findAll('database-type');

    dbPromise.then(function(types) {
      me.controllerFor('tools.databases.add-user').set('types', types);
    });

    return dbPromise;
  }
});
