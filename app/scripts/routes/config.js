Genesis.ConfigRoute = Ember.Route.extend({
  model: function() {
    return Ember.RSVP.hash({
      config: $.getJSON(Genesis.Config.krakenHost+'/config'),
      hostname: $.getJSON(Genesis.Config.krakenHost+'/config/hostname'),
      timezone: $.getJSON(Genesis.Config.krakenHost+'/config/timezone'),
      datetime: $.getJSON(Genesis.Config.krakenHost+'/config/datetime')
    });
  },
  setupController: function(controller, model) {
    controller.set('model', model);
    controller.set('hostname', model.hostname.hostname);
    controller.set('tzRegion', model.timezone.timezone.region);
    controller.set('tzZone', model.timezone.timezone.zone);
  }
});
