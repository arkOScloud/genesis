import Ember from "ember";


export default Ember.Route.extend({
  model: function() {
    return Ember.RSVP.hash({
      policies: this.get('store').find('policy'),
      jails: this.get('store').find('jail')
    });
  }
});
