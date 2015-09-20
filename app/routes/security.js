import Ember from "ember";
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  model: function() {
    return Ember.RSVP.hash({
      policies: this.get('store').findAll('policy'),
      jails: this.get('store').findAll('jail')
    });
  }
});
