import Ember from 'ember';
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  model: function() {
    return Ember.RSVP.hash({
      users: this.get('store').findAll('user'),
      shareTypes: this.get('store').findAll('shareType')
    });
  },
  renderTemplate: function() {
    this.render('tools.shares.shares.add', { into: 'application' });
  }
});
