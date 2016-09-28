import Ember from "ember";
import ENV from "../config/environment";


export default Ember.Controller.extend({
  showingStacktrace: function() {
    return false;
  }.property("model"),
  showingCrashReport: function() {
    return false;
  }.property("model"),
  networkError: function() {
    return typeof this.get("model.report") === "undefined";
  }.property("model"),
  stackTrace: function() {
    if (!this.get("networkError")) {
      return this.get("model.stack");
    } else {
      return null;
    }
  }.property("networkError", "model"),
  crashReport: function() {
    if (!this.get("networkError")) {
      return this.get("model.report");
    } else {
      return null;
    }
  }.property("networkError", "model"),
  actions: {
    submitCrashReport: function() {
      var self = this,
          data = this.get("model");
      Ember.$.ajax(`${ENV.APP.GRMHost}/api/v1/error`, {
        type: "POST",
        data: JSON.stringify({
          summary: data.message,
          trace: data.stack,
          version: data.version,
          arch: data.arch,
          report: data.report
        }),
        contentType: 'application/json',
        success: function(j) {
          self.notifications.new("success", j.message);
          Ember.$("#reportbtn").addClass("disabled");
        },
        error: function(j) {
          self.notifications.new("error", j.message);
        }
      });
    },
    showStacktrace: function() {
      this.set("showingStacktrace", true);
    },
    showCrashReport: function() {
      this.set("showingCrashReport", true);
    }
  }
});
