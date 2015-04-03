import Ember from "ember";


export default Ember.ObjectController.extend({
  needs: 'domain',
  actions: {
    save: function(){
      var self = this;
      if (this.store.hasRecordForId('domain', this.get('name'))) {
        this.message.danger('This domain already exists');
        return false;
      };
      var domain = this.store.createRecord('domain', {
        id: this.get('name')
      });
      var promise = domain.save();
      promise.then(function(){}, function(e){
        if (e.status == 500) self.transitionToRoute("error", e);
        domain.deleteRecord();
      });
    },
    removeModal: function(){
      this.set('name', '');
      return true;
    }
  }
});
