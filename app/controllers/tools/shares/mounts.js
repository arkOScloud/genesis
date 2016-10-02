import Ember from 'ember';

export default Ember.Controller.extend({
  breadCrumb: {name: 'File Shares', icon: 'external share'},
  actions: {
    openModal: function(name, mount) {
      this.set('selectedMount', mount);
      Ember.$('.ui.' + name + '.modal').modal('show');
    },
    deleteMount: function() {
      this.get('selectedMount').destroyRecord();
      this.set('selectedMount', null);
    }
  }
});
