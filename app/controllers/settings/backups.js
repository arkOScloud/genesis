import Ember from "ember";
import ENV from "../../config/environment";


export default Ember.ObjectController.extend({
  breadCrumb: {name: 'Recovery', icon: 'history'},
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
      Ember.$.ajax(`${ENV.APP.krakenHost}/api/backups/${type}`, {
        type: 'POST',
        data: JSON.stringify({backup: this.get("selectedBackupType")}),
        contentType: 'application/json',
      })
        .error(function(e) {
          if (e.status === 500) {
            self.transitionToRoute("error", e);
          }
        });
    },
    selectType: function(item) {
      Ember.$('#backup-menu > a').removeClass('active');
      Ember.$('#'+item).addClass('active');
      this.set('selectedBackupType', item !== "all" ? item : "");
    },
    openModal: function(name, backup) {
      this.set('selectedBackup', backup);
      Ember.$('.ui.' + name + '.modal').modal('show');
    },
    deleteBackup: function() {
      this.get('selectedBackup').destroyRecord();
      this.set('selectedBackup', null);
    },
    restoreBackup: function() {
      this.set('selectedBackup.isReady', false);
      this.get('selectedBackup').save();
      this.set('selectedBackup', null);
    },
    clearModal: function() {
      this.set('selectedBackup', null);
    }
  }
});
