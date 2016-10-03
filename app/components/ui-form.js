import Ember from 'ember';


export default Ember.Component.extend({
  tagName: 'form',
  classNames: ['ui', 'form'],
  setupForm: function() {
    var self = this;
    Ember.$('#' + this.get('elementId') + ' .input').keypress(function(e) {
      if (e.which === 13) {
        self.send('save');
        return false;
      }
    });
  }.on('didInsertElement'),
  actions: {
    save: function() {
      var self = this;
      if (this.get('fields')) {
        Ember.$('#' + this.get('elementId')).form({
          fields: this.get('fields'),
          inline: true,
          keyboardShortcuts: false,
          onSuccess: function() {
            self.set('isSubmitting', true);
            self.sendAction('onSubmit');
          }
        });
        Ember.$('#' + this.get('elementId')).form('validate form');
      } else {
        this.sendAction('onSubmit');
      }
    },
    cancel: function() {
      this.sendAction('onCancel');
    }
  }
});
