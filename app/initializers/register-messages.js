import Ember from "ember";


export function initialize(container, application) {
  var Message = Ember.Object.extend();
  var Messager = Ember.ArrayProxy.extend({
    content: Ember.A(),
    timeout: 5000,
    pushObject: function(object) {
      object.typeClass = 'alert-' + object.type;
      Ember.run.later(function() {
        if (object.dismissable && ["info", "success"].indexOf(object.type)>=0) {
          Ember.$('#'+object.id).alert('close');
        }
      }, this.get('timeout'));
      var exists = this.content.filterBy('id', object.id);
      if (exists.length) {
        exists[0].set('type', object.type);
        exists[0].set('typeClass', object.typeClass);
        exists[0].set('icon', object.icon);
        exists[0].set('message', object.message);
        exists[0].set('headline', object.headline);
        exists[0].set('dismissable', object.dismissable);
      } else {
        object = Message.create(object);
        this._super(object);
      }
    },
    danger: function(message, id, dismissable, headline) {
      id = id || Math.random().toString(36).substring(10);
      this.pushObject({
        id: id,
        type: 'danger',
        icon: 'fa fa-exclamation-circle',
        message: message,
        headline: headline,
        dismissable: typeof dismissable !== 'undefined' ? dismissable : true
      });
    },
    warning: function(message, id, dismissable, headline) {
      id = id || Math.random().toString(36).substring(10);
      this.pushObject({
        id: id,
        type: 'warning',
        icon: 'fa fa-exclamation-triangle',
        message: message,
        headline: headline,
        dismissable: typeof dismissable !== 'undefined' ? dismissable : true
      });
    },
    info: function(message, id, dismissable, headline) {
      id = id || Math.random().toString(36).substring(10);
      this.pushObject({
        id: id,
        type: 'info',
        icon: 'fa fa-info-circle',
        message: message,
        headline: headline,
        dismissable: typeof dismissable !== 'undefined' ? dismissable : true
      });
    },
    success: function(message, id, dismissable, headline) {
      id = id || Math.random().toString(36).substring(10);
      this.pushObject({
        id: id,
        type: 'success',
        icon: 'fa fa-thumbs-up',
        message: message,
        headline: headline,
        dismissable: typeof dismissable !== 'undefined' ? dismissable : true
      });
    }
  });
  application.register('message:main', Messager);
};
