import Ember from 'ember';

export default Ember.Component.extend({
  classNames: ["ui", "dropdown", "item"],
  initializeElement: function() {
    Ember.$('#'+this.get('elementId')).dropdown();
  }.on('didInsertElement')
});
