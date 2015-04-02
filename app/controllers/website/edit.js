import Ember from "ember";
import ENV from "../../config/environment";


export default Ember.ObjectController.extend({
  newName: function() {
    return this.get('model').get('id');
  }.property('model'),
  newAddr: function() {
    return this.get('model').get('addr');
  }.property('model'),
  newPort: function() {
    return this.get('model').get('port');
  }.property('model'),
  actions: {
    save: function() {
      var site = this.get('model');
      site.setProperties({
        addr: this.get('newAddr'),
        port: this.get('newPort'),
        newName: (this.get('newName')!=site.get('id'))?this.get('newName'):'',
        isReady: false
      });
      site.save();
    },
    siteAction: function(action) {
      var self = this;
      $.ajax({
        url: ENV.APP.krakenHost+'/websites/actions/'+this.get("model.id")+"/"+action,
        type: "POST"
      })
      .success(function(){
        self.message.success("Action completed successfully");
      })
      .error(function(e){
        self.message.danger("Action did not complete: "+e.responseJSON.message);
      });
    }
  }
});