import Ember from "ember";


export default Ember.Component.extend({
  stepId: function() {
    return 'wizardstep'+this.step;
  }.property(),
  hidden: function() {
    return this.step!=1?'display:none;':'';
  }.property()
});
