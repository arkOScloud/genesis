import Ember from "ember";
import ENV from "../../config/environment";


export default Ember.ObjectController.extend({
  name: '',
  actions: {
    save: function(){
      var uploader = EmberUploader.Uploader.create({
        url: ENV.APP.krakenHost+'/certs'
      });
      var files = [$('input[name="cert"]')[0].files[0],
                   $('input[name="key"]')[0].files[0]];
      if ($('input[name="chain"]')[0].files.length) {
        files.push($('input[name="chain"]')[0].files[0]);
      };
      uploader.upload(files, {id: this.get('name')});
    },
    removeModal: function(){
      this.set('name', '');
      return true;
    }
  }
});
