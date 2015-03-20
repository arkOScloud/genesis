import Ember from "ember";


export default Ember.ObjectController.extend({
  name: '',
  actions: {
    save: function(){
      var db = this.store.createRecord('database', {
        name: this.get('name'),
        typeId: this.get('type'),
        typeName: this.get('type')
      });
      var promise = db.save();
      promise.then(function(){}, function(){
        db.deleteRecord();
      });
    },
    removeModal: function(){
      this.set('name', '');
      this.set('type', '');
      return true;
    }
  }
});
