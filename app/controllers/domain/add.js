import Ember from "ember";


export default Ember.ObjectController.extend({
  needs: 'domain',
  actions: {
    save: function(){
      if (this.store.hasRecordForId('domain', this.get('name'))) {
        this.message.danger('This domain already exists');
        return false;
      };
      var domain = this.store.createRecord('domain', {
        id: this.get('name')
      });
      var promise = domain.save();
      promise.then(function(){}, function(){
        domain.deleteRecord();
      });
    },
    removeModal: function(){
      this.set('name', '');
      return true;
    }
  }
});
