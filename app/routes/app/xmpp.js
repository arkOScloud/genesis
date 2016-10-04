import Ember from "ember";
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  model: function() {
    return Ember.RSVP.hash({
      domains: this.get('store').findAll('domain'),
      service: this.get('store').find('service', 'prosody')
    });
  }
});
