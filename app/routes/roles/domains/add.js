import Ember from 'ember';

export default Ember.Route.extend({
  renderTemplate: function() {
    this.render('roles.domains.add', { into: 'application' });
  }
});
