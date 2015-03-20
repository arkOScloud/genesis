import Ember from "ember";


export default Ember.ObjectController.extend({
  newName: function() {
    return this.get('model').get('id');
  }.property('model'),
  newAddr: function() {
    return this.get('model').get('addr');
  }.property('model'),
  newPort: function() {
    return this.get('model').get('port');
  }.property('model'),
  actions: {
    save: function() {
      var site = this.get('model');
      site.setProperties({
        addr: this.get('newAddr'),
        port: this.get('newPort'),
        newName: (this.get('newName')!=site.get('id'))?this.get('newName'):'',
        isReady: false
      });
      site.save();
    }
  }
});
