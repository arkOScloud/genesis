import Ember from "ember";
import ENV from "../config/environment";
import fieldValidator from "../utils/field-validator";
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  model: function() {
    return Ember.RSVP.hash({
      apps: this.get("store").find("app"),
      config: $.getJSON(ENV.APP.krakenHost+"/config")
    });
  },
  step: 1,
  renderTemplate: function(controller, model) {
    this._super(controller, model);
    this.render("firstrun/step-1", {into: "firstrun", outlet: "steps", model: model});
  },
  renderStep: function() {
    var step = this.get("step");
    this.render("firstrun/step-"+step, {
      into: "firstrun",
      outlet: "steps"
    });
  }.observes("step"),
  actions: {
    previousStep: function() {
      this.decrementProperty("step");
    },
    nextStep: function() {
      var self = this;
      if (!$('.ui-firstrun-container .form-group').length) return this.incrementProperty("step");
      fieldValidator(".ui-firstrun-container");
      setTimeout(function(){
        if ($('.ui-firstrun-container .form-group.has-error').length == 0) {
          self.incrementProperty("step");
        };
      }, 1000);
    },
    finish: function() {
      var self = this;
      $.ajax({
        url: ENV.APP.krakenHost+'/config',
        type: 'PATCH',
        data: JSON.stringify({config: {genesis: {anonymous: false, firstrun: true}}}),
        contentType: 'application/json',
        processData: false,
        success: function() {
          self.transitionTo("index");
        }
      });
    }
  }
});
