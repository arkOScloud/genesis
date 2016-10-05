import Ember from "ember";
import ENV from "../config/environment";
import ApplicationRouteMixin from 'simple-auth/mixins/application-route-mixin';


export default Ember.Route.extend(ApplicationRouteMixin, {
  afterModel: function() {
    this.autoFirstRun();
  },
  autoFirstRun: function() {
    var self = this;
    self.controllerFor('login').set('currentlyLoading', true);
    Ember.run.next(self, function() {
      if (typeof ENV.APP.needsFirstRun === 'undefined') {
        self.autoFirstRun();
      } else if (ENV.APP.needsFirstRun && !this.get('session.isAuthenticated')) {
        var authenticator = 'simple-auth-authenticator:jwt';
        this.get('session').authenticate(
          authenticator, {identification: "", password: ""}
        );
      } else if (ENV.APP.needsFirstRun && !this.get('routeName').startsWith('firstrun')) {
        self.transitionTo('firstrun.start');
      } else if (!ENV.APP.needsFirstRun) {
        self.controllerFor('login').set('currentlyLoading', false);
      }
    });
  },
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
      if (!transition.targetName.startsWith("firstrun") && ENV.APP.needsFirstRun) {
        transition.abort();
        this.transitionTo('firstrun.start');
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
