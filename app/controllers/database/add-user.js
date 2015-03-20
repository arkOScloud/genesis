import Ember from "ember";


export default Ember.ObjectController.extend({
  name: '',
  userTypes: function(){
    return this.get('types').filterProperty('supportsUsers', true);
  }.property('types'),
  actions: {
    save: function(){
      var db = this.store.createRecord('databaseUser', {
        name: this.get('name'),
        typeId: this.get('type'),
        passwd: this.get('passwd')
      });
      var promise = db.save();
      promise.then(function(){}, function(){
        db.deleteRecord();
      });
    },
    removeModal: function(){
      this.set('name', '');
      this.set('type', '');
      this.set('passwd', '');
      this.set('passwdb', '');
      return true;
    }
  }
});
