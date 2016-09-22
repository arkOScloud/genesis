import Ember from 'ember';

export default Ember.Route.extend({
  renderTemplate: function() {
    this.render('tools.databases.user-edit', { into: 'application' });
  },
  afterModel: function() {
    var me = this;
    var dbPromise = this.store.findAll('database');

    dbPromise.then(function(dbs) {
      me.controllerFor('tools.databases.user-edit').set('dbs', dbs);
    });

    return dbPromise;
  }
});
