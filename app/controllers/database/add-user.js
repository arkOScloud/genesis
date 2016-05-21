import Ember from "ember";


export default Ember.ObjectController.extend({
  name: '',
  userTypes: function(){
    return this.get('types').filterProperty('supportsUsers', true);
  }.property('types'),
  actions: {
    save: function(){
      var self = this;
      var db = this.store.createRecord('databaseUser', {
        id: this.get('id'),
        typeId: this.get('type.id'),
        passwd: this.get('passwd')
      });
      var promise = db.save();
      promise.then(function(){}, function(e){
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        }
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
