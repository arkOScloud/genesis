import Ember from "ember";
import ENV from "../../../config/environment";
import handleModelError from '../../../utils/handle-model-error';


export default Ember.ObjectController.extend({
  breadCrumb: {name: 'File Sync', icon: 'refresh'},
  actions: {
    saveSettings: function() {
      var self = this,
         config = this.get('model.config');
      Ember.$.ajax(`${ENV.APP.krakenHost}/api/apps/syncthing/config`, {
        type: 'POST',
        data: JSON.stringify({config: config}),
        contentType: 'application/json'
      })
        .done(function() {
          self.notifications.new("success", "Configuration saved successfully");
        })
        .fail(function(e) {
          handleModelError(self, e);
        });
    }
  }
});
