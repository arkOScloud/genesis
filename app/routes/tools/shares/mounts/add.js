import Ember from 'ember';
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  model: function() {
    return this.get('store').findAll('shareType');
  },
  renderTemplate: function() {
    this.render('tools.shares.mounts.add', { into: 'application' });
  }
});
