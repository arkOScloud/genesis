import Ember from "ember";


export default Ember.ObjectController.extend({
  actions: {
    save: function() {
      var fs = this.get('model');
      fs.set('operation', 'mount');
      fs.set('isReady', false);
      fs.save();
    },
    removeModal: function(){
      this.get('model').setProperties({
        operation: '',
        passwd: ''
      });
      return true;
    }
  }
});
