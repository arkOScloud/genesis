Genesis.ApplicationAdapter = DS.RESTAdapter.extend({
    host: Genesis.Config.krakenHost,
    pathForType: function(type) {
      var stype = this._super(type);
      return Ember.String.decamelize(stype);
    },
    ajaxError: function(jqXHR) {
      var error = this._super(jqXHR);
      if (jqXHR && jqXHR.status === 422) {
        var jsonPayload = Ember.$.parseJSON(jqXHR.responseText);
        if (jsonPayload && jsonPayload.message) {
          Genesis.addMessage("error", jsonPayload.message);
          delete jsonPayload.message;
        } else if (jsonPayload && jsonPayload.messages) {
          jsonPayload.messages.forEach(function(e) {
            Genesis.addMessage("error", e.message);
          })
          delete jsonPayload.messages;
        };
      } else {
        return error;
      }
    },
    ajaxSuccess: function(jqXHR, jsonPayload) {
      if (jsonPayload && jsonPayload.message) {
        var msgType = String(jqXHR.status).charAt(0)?"success":"warn";
        Genesis.addMessage(msgType, jsonPayload.message);
        delete jsonPayload.message;
      } else if (jsonPayload && jsonPayload.messages) {
        jsonPayload.messages.forEach(function(e) {
          Genesis.addMessage("success", e.message);
        })
        delete jsonPayload.messages;
      };
      return jsonPayload;
    }
});
