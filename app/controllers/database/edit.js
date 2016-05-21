import Ember from "ember";
import ENV from "../../config/environment";


export default Ember.ObjectController.extend({
  actions: {
    execute: function(){
      var self = this;
      Ember.$.ajax({
        url: ENV.APP.krakenHost+'/api/databases/'+this.get('model').get('id'),
        data: JSON.stringify({"database": {"execute": this.get('execInput')}}),
        type: 'PUT',
        contentType: 'application/json',
        processData: false,
        success: function(j){
          self.set('execOutput', j.database.result);
        },
        error: function(e){
          if (e.status === 500) {
            self.transitionToRoute("error", e);
          }
        }
      });
    },
    removeModal: function(){
      this.set('execInput', '');
      this.set('execOutput', '');
      return true;
    }
  }
});
