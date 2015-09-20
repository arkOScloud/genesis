import Ember from "ember";
import ENV from "../../config/environment";


export default Ember.ObjectController.extend({
  output: "",
  actions: {
    save: function() {
      if (this.get("output")) {
        var self = this,
            file = this.get("model"),
            output = this.get("output");
        Ember.$.ajax({
          url: ENV.APP.krakenHost+'/api/files/'+file.id,
          type: "PUT",
          data: JSON.stringify({file:{path:file.path,data:output,operation:"edit"}}),
          contentType: 'application/json',
          processData: false,
          success: function() {
            self.message.success("File saved successfully");
          },
          error: function(e) {
            if (e.status === 500) {
              self.transitionToRoute("error", e);
            }
          }
        });
      }
    }
  }
});
