import Ember from 'ember';
import ENV from "../../../config/environment";


export default Ember.Controller.extend({
  breadCrumb: Ember.computed("model.id", {
    get() {
      return {name: this.get("model.id"), icon: 'fa-database'};
    }
  }),
  actions: {
    execute: function(){
      var self = this;
      if (!this.get('execInput')) {
        return false;
      }
      Ember.$.ajax({
        url: ENV.APP.krakenHost+'/api/databases/'+this.get('model.id'),
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
    openModal: function(name) {
      Ember.$('.ui.' + name + '.modal').modal('show');
    },
    deleteDb: function() {
      var self = this;
      Ember.$('.ui.delete-db.modal').modal('hide', function() {
        self.get('model').destroyRecord();
        self.transitionToRoute('tools.databases');
      });
    }
  }
});