import Ember from "ember";
import ENV from "../../config/environment";


export default Ember.ObjectController.extend({
  name: '',
  actions: {
    save: function(){
      var self = this;
      var uploader = EmberUploader.Uploader.create({
        url: ENV.APP.krakenHost+'/api/certs'
      });
      var files = [$('input[name="cert"]')[0].files[0],
                   $('input[name="key"]')[0].files[0]];
      if ($('input[name="chain"]')[0].files.length) {
        files.push($('input[name="chain"]')[0].files[0]);
      };
      var promise = uploader.upload(files, {id: this.get('name')});
      promise.then(function(){}, function(e){
        if (e.status == 500) self.transitionToRoute("error", e);
      });
    },
    removeModal: function(){
      this.set('name', '');
      return true;
    }
  }
});
