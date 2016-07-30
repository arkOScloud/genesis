import Ember from "ember";
import ENV from "../config/environment";
import timezones from "../utils/timezones";
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  model: function() {
    return Ember.RSVP.hash({
      config: Ember.$.getJSON(ENV.APP.krakenHost+'/api/config'),
      datetime: Ember.$.getJSON(ENV.APP.krakenHost+'/api/config/datetime'),
      users: this.get("store").findAll("user"),
      ssh: this.get("store").findAll("sshKey")
    });
  },
  setupController: function(controller, model) {
    controller.set('model', model);
    controller.set('config', model.config.config);
    controller.set('hostname', model.config.hostname);
    controller.set('tzRegion', timezones.filter(function (o){return o.region === model.config.timezone.region;}));
    controller.set('tzRegionName', model.config.timezone.region);
    controller.set('tzZone', model.config.timezone.zone);
  },
  actions: {
    updateTime: function() {
      var self = this;
      Ember.$.ajax({
        url: ENV.APP.krakenHost+'/api/config/datetime',
        type: 'PUT',
        success: function() {
          self.refresh();
          self.message.success("Time updated successfully");
        },
        error: function(e) {
          if (e.status === 500) {
            self.transitionTo("error", e);
          }
        }
      });
    },
    delete: function(model) {
      model.destroyRecord();
    }
  }
});
