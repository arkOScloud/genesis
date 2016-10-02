import Ember from 'ember';

export default Ember.Controller.extend({
  breadCrumb: {name: 'File Shares', icon: 'external share'},
  actions: {
    openModal: function(name, share) {
      this.set('selectedShare', share);
      Ember.$('.ui.' + name + '.modal').modal('show');
    },
    deleteShare: function() {
      this.get('selectedShare').destroyRecord();
      this.set('selectedShare', null);
    }
  }
});
