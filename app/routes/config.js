import Ember from "ember";
import ENV from "../config/environment";


export default Ember.Route.extend({
  model: function() {
    return Ember.RSVP.hash({
      config: $.getJSON(ENV.APP.krakenHost+'/config'),
      hostname: $.getJSON(ENV.APP.krakenHost+'/config/hostname'),
      timezone: $.getJSON(ENV.APP.krakenHost+'/config/timezone'),
      datetime: $.getJSON(ENV.APP.krakenHost+'/config/datetime')
    });
  },
  setupController: function(controller, model) {
    controller.set('model', model);
    controller.set('config', model.config.config);
    controller.set('hostname', model.hostname.hostname);
    controller.set('tzRegion', model.timezone.timezone.region);
    controller.set('tzZone', model.timezone.timezone.zone);
  }
});
