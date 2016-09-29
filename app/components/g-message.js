import Ember from "ember";


export default Ember.Component.extend({
  actions: {
    dismiss: function() {
      var self = this;
      Ember.$(`#notification-box-${self.get('msg').id}`).transition('fade', function() {
        self.notifications.remove(self.get('msg'));
      });
    }
  }
});
