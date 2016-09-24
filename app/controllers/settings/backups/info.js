import Ember from 'ember';

export default Ember.Controller.extend({
  actions: {
    openModal: function(name) {
      Ember.$('.ui.' + name + '.modal').modal('show');
    },
    deleteBackup: function() {
      var self = this;
      Ember.$('.ui.delete-backup.modal').modal('hide', function() {
        self.get('model').destroyRecord();
        self.transitionToRoute('settings.backups');
      });
    },
    restoreBackup: function() {
      var self = this;
      this.set('model.isReady', false);
      this.get('model').save();
      Ember.$('.ui.delete-backup.modal').modal('hide', function() {
        self.transitionToRoute('settings.backups');
      });
    }
  }
});
