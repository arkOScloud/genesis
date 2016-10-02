import Ember from 'ember';
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  model: function() {
    return Ember.RSVP.hash({
      mounts: this.get('store').findAll('mount'),
      types: this.get('store').findAll('share-type')
    });
  }
});
