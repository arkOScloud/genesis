import Ember from "ember";


export default Ember.Component.extend({
  classNames: 'message-box-wr',
  messages: Ember.computed.alias('message')
});
