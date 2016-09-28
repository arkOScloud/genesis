import Ember from "ember";


export default Ember.Component.extend({
  classNames: 'message-box-wr',
  messages: Ember.computed.filter('notifications.items', function(item) {
    return !item.noFlash;
  })
});
