import Ember from "ember";
import ENV from "../../config/environment";


export default Ember.ObjectController.extend({
  actionsToTake: ["No action", "Grant all permissions", "Revoke all permissions"],
  availableDbs: function(){
    return this.get('model').get('extra').dbs.filterProperty('typeId', this.get('model').get('typeId'));
  }.property('dbs'),
  actions: {
    save: function(){
      var self = this,
          actionToTake = "";
      if (this.get('action') === "Grant all permissions") {
        actionToTake = "grant";
      } else if (this.get('action') === "Revoke all permissions") {
        actionToTake = "revoke";
      } else {
        return false;
      }
      Ember.$.ajax({
        url: ENV.APP.krakenHost+'/api/database_users/'+this.get('model').get('id'),
        data: JSON.stringify({"database_user": {"operation": actionToTake, "database": this.get('database')}}),
        type: 'PUT',
        contentType: 'application/json',
        processData: false,
        error: function(e) {
          if (e.status === 500) {
            self.transitionToRoute("error", e);
          }
        }
      });
    },
    removeModal: function(){
      this.set('action', '');
      this.set('database', '');
      return true;
    }
  }
});
