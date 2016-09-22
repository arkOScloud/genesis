import Ember from 'ember';
import ENV from "../../../config/environment";


export default Ember.Controller.extend({
  breadCrumb: Ember.computed("model.id", {
    get() {
      return {name: this.get("model.id"), icon: 'fa-user'};
    }
  }),
  action: "No action",
  actionsToTake: ["No action", "Grant all permissions", "Revoke all permissions"],
  availableDbs: function(){
    return this.get('dbs').filterProperty('typeId', this.get('model').get('typeId'));
  }.property('dbs'),
  actions: {
    save: function(){
      var self = this,
          actionToTake = "";
      if (this.get('action').startsWith("Grant")) {
        actionToTake = "grant";
      } else if (this.get('action').startsWith("Revoke")) {
        actionToTake = "revoke";
      } else {
        return false;
      }
      Ember.$.ajax({
        url: ENV.APP.krakenHost+'/api/database_users/'+this.get('model').get('id'),
        data: JSON.stringify({"database_user": {"operation": actionToTake, "database": this.get('selectedDb')}}),
        type: 'PUT',
        contentType: 'application/json',
        processData: false,
        error: function(e) {
          if (e.status === 500) {
            self.transitionToRoute("error", e);
          }
        },
        success: function() {
          self.model.reload();
        }
      });
    },
    openModal: function(name) {
      Ember.$('.ui.' + name + '.modal').modal('show');
    },
    deleteUser: function() {
      var self = this;
      this.get('model').destroyRecord();
      Ember.$('.ui.delete-user.modal').modal('hide', function() {
        self.transitionToRoute('tools.databases');
      });
    }
  }
});
