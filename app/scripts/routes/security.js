Genesis.SecurityRoute = Ember.Route.extend({
  model: function() {
    return Ember.RSVP.hash({
      policies: this.get('store').find('policy'),
      jails: this.get('store').find('jail')
    });
  }
});
