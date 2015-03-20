import Ember from "ember";
import ENV from "../../config/environment";


export default Ember.ObjectController.extend({
  actionsToTake: ["No action", "Grant all permissions", "Revoke all permissions"],
  availableDbs: function(){
    return this.get('model').get('extra').dbs.filterProperty('typeId', this.get('model').get('typeId'));
  }.property('dbs'),
  actions: {
    save: function(){
      var self = this;
      if (this.get('action') == "Grant all permissions") {
        actionToTake = "grant"
      } else if (this.get('action') == "Revoke all permissions") {
        actionToTake = "revoke"
      } else {
        return false;
      };
      var exec = $.ajax({
        url: ENV.APP.krakenHost+'/database_users/'+this.get('model').get('id'),
        data: JSON.stringify({"database_user": {"operation": actionToTake, "database": this.get('database')}}),
        type: 'PUT',
        contentType: 'application/json',
        processData: false
      });
    },
    removeModal: function(){
      this.set('action', '');
      this.set('database', '');
      return true;
    }
  }
});
