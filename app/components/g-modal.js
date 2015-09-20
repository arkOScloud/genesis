import Ember from "ember";
import fieldValidator from "../utils/field-validator";


export default Ember.Component.extend({
  okWord: "OK",
  cancelWord: "Cancel",
  actions: {
    ok: function() {
      if (!this.confirm) {
        fieldValidator('.modal');
        var self = this;
        setTimeout(function(){
          if (self.$('.modal .form-group.has-error').length === 0) {
            self.$('.modal').modal('hide');
            self.sendAction('ok');
          }
        }, 1000);
      } else {
        this.$('.modal').modal('hide');
        this.sendAction('ok', this.get('model'));
      }
    }
  },
  show: function() {
    this.$('.modal').modal().on('hidden.bs.modal', function() {
      this.sendAction('close');
    }.bind(this));
  }.on('didInsertElement')
});
