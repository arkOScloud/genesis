import Ember from 'ember';
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  model: function() {
    return this.store.findAll('user');
  },
  renderTemplate: function() {
    this.render('app.radicale.new-book', { into: 'application' });
  }
});
