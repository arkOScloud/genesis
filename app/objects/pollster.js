import Ember from 'ember';


var Pollster = Ember.Object.extend({
  interval: function() {
    return 2000; // Time between polls (in ms)
  }.property().readOnly(),
  schedule: function(f, args) {
    return Ember.run.later(this, function() {
      f.apply(this, [args]);
      this.set('timer', this.schedule(f, args));
    }, this.get('interval'));
  },
  stop: function() {
    Ember.run.cancel(this.get('timer'));
  },
  start: function() {
    this.set('timer', this.schedule(this.get('onPoll'), this.get('args')));
  },
  onPoll: function(){
    // Do some work
  }
});

export default Pollster;
