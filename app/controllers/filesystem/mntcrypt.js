import Ember from "ember";


export default Ember.ObjectController.extend({
  actions: {
    save: function() {
      var self = this;
      var fs = this.get('model');
      fs.set('operation', 'mount');
      fs.set('isReady', false);
      var promise = fs.save();
      promise.then(function(){}, function(e){
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        }
      });
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
