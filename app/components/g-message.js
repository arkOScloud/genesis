import Ember from "ember";


export default Ember.Component.extend({
  actions: {
    dismiss: function() {
      var self = this;
      Ember.$('#'+this.get('msg').id).transition('fade', function() {
        self.message.removeObject(self.get('msg'));
      });
    }
  }
});
