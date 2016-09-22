import Ember from 'ember';

export default Ember.Route.extend({
  renderTemplate: function() {
    this.render('tools.databases.add', { into: 'application' });
  },
  afterModel: function() {
    var me = this;
    var dbPromise = this.store.findAll('database-type');

    dbPromise.then(function(types) {
      me.controllerFor('tools.databases.add').set('types', types);
    });

    return dbPromise;
  }
});
