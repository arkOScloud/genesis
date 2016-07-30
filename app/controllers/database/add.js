import Ember from "ember";


export default Ember.ObjectController.extend({
  name: '',
  actions: {
    save: function(){
      var self = this;
      var db = this.store.createRecord('database', {
        id: this.get('id'),
        typeId: this.get('type.id')
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
      return true;
    }
  }
});
