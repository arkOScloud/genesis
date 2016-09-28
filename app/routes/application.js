import Ember from "ember";
import ENV from "../config/environment";
import ApplicationRouteMixin from 'simple-auth/mixins/application-route-mixin';


export default Ember.Route.extend(ApplicationRouteMixin, {
  actions: {
    sessionAuthenticationSucceeded: function() {
      this.controllerFor("login").set("isLoading", false);
      this._super();
    },
    sessionAuthenticationFailed: function(err) {
      var msg = "";
      if (err.message === "Invalid credentials") {
        msg = "Username or password incorrect.";
      } else if (err.message === "Not an admin user") {
        msg = "This user does not have administration rights.";
      } else {
        msg = "Unknown error, please check server.";
      }
      this.controllerFor("login").set("loginMessage", msg);
      this.controllerFor("login").set("isLoading", false);
    },
    willTransition: function(transition) {
      if (transition.targetName !== "firstrun" && ENV.APP.needsFirstRun) {
        transition.abort();
        this.transitionTo('firstrun');
      }
    },
    error: function() {
      return true;
    },
    shutdown: function() {
      Ember.$.ajax(`${ENV.APP.krakenHost}/api/system/shutdown`, {type: 'POST'});
    },
    reload: function() {
      Ember.$.ajax(`${ENV.APP.krakenHost}/api/system/reload`, {type: 'POST'});
    },
    reboot: function() {
      Ember.$.ajax(`${ENV.APP.krakenHost}/api/system/reboot`, {type: 'POST'});
    }
  }
});
