import Ember from 'ember';

export default Ember.Controller.extend({
  breadCrumb: {name: 'File Sync', icon: 'refresh'},
  actions: {
    openModal: function(name, folder) {
      this.set('selectedFolder', folder);
      Ember.$('.ui.' + name + '.modal').modal('show');
    },
    deleteFolder: function() {
      var self = this;
      Ember.$('.ui.delete-folder.modal').modal('hide', function() {
        self.get('selectedFolder').destroyRecord();
        self.transitionToRoute('app.syncthing.folders');
      });
    }
  }
});
