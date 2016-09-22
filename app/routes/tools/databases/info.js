import Ember from 'ember';

export default Ember.Route.extend({
  renderTemplate: function() {
    this.render('tools.databases.info', { into: 'application' });
  }
});
