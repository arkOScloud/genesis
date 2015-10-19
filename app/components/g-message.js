import Ember from "ember";


export default Ember.Component.extend({
  didInsertElement: function() {
    var self = this;
    Ember.$('#'+self.get('msg').id).on('closed.bs.alert', function() {
      self.message.removeObject(self.get('msg'));
    });
  },
  actions: {
    dismiss: function() {
      Ember.$('#'+this.get('msg').id).alert('close');
    }
  }
});
