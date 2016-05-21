import Ember from "ember";
import ENV from "../config/environment";


export default Ember.ObjectController.extend({
  selectedBackupType: "",
  selectedBackups: Ember.computed.filter('model.backups', function(i) {
    if (this.get('selectedBackupType') === "") {
      return true;
    }
    return i.get('pid') === this.get('selectedBackupType');
  }).property('model.backups', 'selectedBackupType'),
  actions: {
    backup: function(type) {
      var self = this;
      Ember.$.ajax({
        url: ENV.APP.krakenHost+'/api/backups/'+type,
        type: 'POST',
        error: function(e) {
          if (e.status === 500) {
            self.transitionToRoute("error", e);
          }
        }
      });
    },
    selectType: function(item) {
      Ember.$('.ui-navlist > li').removeClass('active');
      Ember.$('#'+item).addClass('active');
      this.set('selectedBackupType', item !== "all" ? item : "");
    }
  }
});
