import Ember from 'ember';
import ENV from "../config/environment";
/* global moment */


var Message = Ember.Object.extend();

var setIcon = function(lvl) {
  switch(lvl) {
    case "success":
      return "thumbs up";
    case "warning":
      return "exclamation triangle";
    case "error":
      return "exclamation circle";
    default:
      return "info circle";
  }
};

export default Ember.Service.extend({
  items: Ember.A(),
  timeout: 5000,

  init: function() {
    this._super(...arguments);
    var self = this;
    Ember.$.getJSON(`${ENV.APP.krakenHost}/api/notifications`, function(n) {
      n.notifications.forEach(function(m) {
        m = setIcon(m);
        m.noFlash = true;
        if (!ENV.APP.needsFirstRun) {
          self.addItem(m);
        }
      });
    });
  },
  addItem: function(object) {
    if (!object.noFlash) {
      Ember.run.later(function() {
        var box = Ember.$(`#notification-box-${object.id}`);
        if (object.complete && box.is(':visible')) {
          box.transition('fade');
        }
      }, this.get('timeout'));
    }
    if (!object.title) {
      object.title = object.level.capitalize();
    }
    var exists = this.get('items').filterBy('id', object.id);
    if (exists.length) {
      exists[0].setProperties(object);
    } else {
      object = Message.create(object);
      this.get('items').pushObject(object);
    }
  },
  newNotification: function(level, message, title, id, complete, time, internal) {
    id = id || Math.random().toString(36).substring(2);
    time = time || moment();
    this.addItem({
      id: id,
      message_id: id,
      level: level,
      icon: setIcon(level),
      message: message,
      title: title,
      time: time,
      complete: complete || true,
      internal: internal || false
    });
  },
  new: function(level, message, title) {
    var id = Math.random().toString(36).substring(2),
      time = moment();
    this.addItem({
      id: id,
      message_id: id,
      level: level,
      icon: setIcon(level),
      message: message,
      title: title,
      time: time,
      complete: true,
      internal: true
    });
  },
  remove: function(msg) {
    this.get('items').removeObject(msg);
    if (!msg.internal) {
      Ember.$.ajax(`${ENV.APP.krakenHost}/api/notifications/${msg.id}`, {type: 'DELETE'});
    }
  },
  empty: function() {
    this.set('items', Ember.A());
    Ember.$.ajax(`${ENV.APP.krakenHost}/api/notifications`, {type: 'DELETE'});
  }
});
