import Ember from "ember";


export default Ember.ObjectController.extend({
  key: '',
  actions: {
    save: function(){
      var self = this;
      var key = this.store.createRecord('sshKey', {
        user: this.get('keyUser'),
        key: this.get('key')
      });
      var promise = key.save();
      promise.then(function(){}, function(e){
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        }
        key.deleteRecord();
      });
    },
    removeModal: function(){
      this.set('key', '');
      this.set('keyUser', undefined);
      return true;
    }
  }
});
