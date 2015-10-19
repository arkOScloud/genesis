import Ember from "ember";
import ENV from "../../config/environment";
import toB64 from "../../utils/to-b64";
import EmberUploader from 'ember-uploader';


export default Ember.ObjectController.extend({
  needs: ["files"],
  actions: {
    save: function(){
      var self = this,
          cp   = this.get("controllers.files.currentPath") || "/";
      var uploader = EmberUploader.Uploader.create({
        url: ENV.APP.krakenHost+'/api/files/'+toB64(cp)
      });
      var promise = uploader.upload(Ember.$('input[name="file"]')[0].files);
      promise.then(function(j){
        j.files.forEach(function(i) {
          self.get("controllers.files.currentFolder").pushObject(i);
        });
      }, function(e){
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        }
      });
    }
  }
});
