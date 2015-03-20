import Ember from 'ember';


var Pollster = Ember.Object.extend({
  interval: function() {
    return 2000; // Time between polls (in ms)
  }.property().readOnly(),
  schedule: function(f) {
    return Ember.run.later(this, function() {
      f.apply(this);
      this.set('timer', this.schedule(f));
    }, this.get('interval'));
  },
  stop: function() {
    Ember.run.cancel(this.get('timer'));
  },
  start: function() {
    this.set('timer', this.schedule(this.get('onPoll')));
  },
  onPoll: function(){
    // Do some work
  }
});

export default Pollster;
