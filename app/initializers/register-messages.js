import Ember from "ember";


export function initialize(container, application) {
  var Message = Ember.Object.extend();
  var Messager = Ember.ArrayProxy.extend({
    content: Ember.A(),
    timeout: 5000,
    pushObject: function(object) {
      Ember.run.later(function() {
        if (object.dismissable && ["info", "success"].indexOf(object.type)>=0) {
          Ember.$('#'+object.id).transition('fade');
        }
      }, this.get('timeout'));
      if (!object.headline) {
        object.headline = object.type.capitalize();
      }
      var exists = this.content.filterBy('id', object.id);
      if (exists.length) {
        exists[0].set('type', object.type);
        exists[0].set('icon', object.icon);
        exists[0].set('message', object.message);
        exists[0].set('headline', object.headline);
        exists[0].set('dismissable', object.dismissable);
      } else {
        object = Message.create(object);
        this._super(object);
      }
    },
    error: function(message, id, dismissable, headline) {
      id = id || Math.random().toString(36).substring(10);
      this.pushObject({
        id: id,
        type: 'error',
        icon: 'exclamation circle',
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
        icon: 'exclamation triangle',
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
        icon: 'info circle',
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
        icon: 'thumbs up',
        message: message,
        headline: headline,
        dismissable: typeof dismissable !== 'undefined' ? dismissable : true
      });
    }
  });
  application.register('message:main', Messager);
}
