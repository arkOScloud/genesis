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
    return (this.get("model.responseJSON") === undefined);
  }.property("model"),
  stackTrace: function() {
    if (!this.get("networkError")) {
      return this.get("model.responseJSON.stacktrace");
    } else {
      return null;
    }
  }.property("networkError", "model"),
  crashReport: function() {
    if (!this.get("networkError")) {
      return this.get("model.responseJSON.report");
    } else {
      return null;
    }
  }.property("networkError", "model"),
  actions: {
    submitCrashReport: function() {
      var self = this,
          data = this.get("model.responseJSON");
      Ember.$.ajax({
        url: ENV.APP.GRMHost+'/api/v1/error',
        type: "POST",
        data: JSON.stringify({
          summary: data.message,
          trace: data.stacktrace,
          version: data.version,
          arch: data.arch,
          report: data.report
        }),
        contentType: 'application/json',
        processData: false,
        success: function(j) {
          self.message.success(j.message);
          Ember.$("#reportbtn").addClass("disabled");
        },
        error: function(j) {
          self.message.error(j.message);
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
