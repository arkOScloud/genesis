import Ember from 'ember';

export default Ember.Route.extend({
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
