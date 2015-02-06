Genesis.GMessagesComponent = Ember.Component.extend({
  classNames: 'message-box-wr',
  messages: Ember.computed.alias('message')
});

Genesis.GMessageComponent = Ember.Component.extend({
  didInsertElement: function() {
    var self = this;
    $('#'+self.get('msg').id).on('closed.bs.alert', function() {
      self.message.removeObject(self.get('msg'));
    });
  },
  actions: {
    dismiss: function() {
      $('#'+this.get('msg').id).alert('close');
    }
  }
});
