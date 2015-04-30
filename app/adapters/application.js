import Ember from "ember";
import DS from "ember-data";
import ENV from "../config/environment";


export default DS.RESTAdapter.extend({
    host: ENV.APP.krakenHost || "",
    namespace: "api",
    pathForType: function(type) {
      var stype = this._super(type);
      return Ember.String.decamelize(stype);
    },
    ajaxError: function(jqXHR) {
      var self = this,
          error = this._super(jqXHR);
      if (jqXHR && jqXHR.status === 422) {
        var jsonPayload = Ember.$.parseJSON(jqXHR.responseText);
        if (jsonPayload && jsonPayload.message) {
          self.message.danger(jsonPayload.message);
          delete jsonPayload.message;
        } else if (jsonPayload && jsonPayload.messages) {
          jsonPayload.messages.forEach(function(e) {
            self.message.danger(e.message);
          });
          delete jsonPayload.messages;
        };
      } else {
        return error;
      }
    },
    ajaxSuccess: function(jqXHR, jsonPayload) {
      if (jsonPayload && jsonPayload.message) {
        var msgType = String(jqXHR.status).charAt(0);
        if (msgType=="2") {
          if (!ENV.APP.needsFirstRun) this.message.success(jsonPayload.message);
        } else {
          this.message.warning(jsonPayload.message);
        }
        delete jsonPayload.message;
      } else if (jsonPayload && jsonPayload.messages) {
        jsonPayload.messages.forEach(function(e) {
          this.message.success(e.message);
        })
        delete jsonPayload.messages;
      };
      return jsonPayload;
    }
});
