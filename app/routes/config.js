import Ember from "ember";
import ENV from "../config/environment";
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  model: function() {
    return Ember.RSVP.hash({
      config: $.getJSON(ENV.APP.krakenHost+'/config'),
      datetime: $.getJSON(ENV.APP.krakenHost+'/config/datetime'),
      users: this.get("store").find("user"),
      ssh: this.get("store").find("sshKey")
    });
  },
  setupController: function(controller, model) {
    controller.set('model', model);
    controller.set('config', model.config.config);
    controller.set('hostname', model.config.hostname);
    controller.set('tzRegion', model.config.timezone.region);
    controller.set('tzZone', model.config.timezone.zone);
  },
  actions: {
    updateTime: function() {
      var self = this;
      $.ajax({
        url: ENV.APP.krakenHost+'/config/datetime',
        type: 'PUT',
        success: function(j) {
          self.refresh();
          self.message.success("Time updated successfully");
        },
        error: function(e) {
          if (e.status == 500) self.transitionToRoute("error", e);
        }
      });
    },
    delete: function(model) {
      model.destroyRecord();
    }
  }
});
