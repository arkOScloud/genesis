import Ember from 'ember';

export default Ember.Route.extend({
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
