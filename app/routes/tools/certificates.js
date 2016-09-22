import Ember from "ember";
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  model: function() {
    return Ember.RSVP.hash({
      certs: this.get('store').findAll('certificate'),
      auths: this.get('store').findAll('authority')
    });
  }
});
