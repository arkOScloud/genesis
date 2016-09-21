import Ember from "ember";
import ENV from "../config/environment";
import Pollster from "../objects/pollster";
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  getStats: function(self) {
    Ember.$.getJSON(ENV.APP.krakenHost+'/api/system/stats/all').then(function(j) {
      self.set('cpuPct', Math.round(j.cpu));
      self.set('memory', j.ram[0]);
      self.set('memoryPct', j.ram[2]);
      self.set('memoryTotal', j.ram[1]);
      self.set('swap', j.swap[0]);
      self.set('swapPct', Math.round(j.swap[1] / j.swap[0] || 0));
      self.set('swapTotal', j.swap[1]);
      self.set('load1min', j.load[0]);
      self.set('load5min', j.load[1]);
      self.set('load10min', j.load[2]);
      self.set('temp', j.temp || 0);
      self.set('uptimeDays', j.uptime[3]);
      self.set('uptimeHours', j.uptime[2]);
      self.set('uptimeMinutes', j.uptime[1]);
      self.set('uptimeSeconds', j.uptime[0]);
    });
  },
  setupController: function() {
    this.getStats(this.controllerFor('stats'));
    if (Ember.isNone(this.get('pollster'))) {
      var p = Pollster.extend({
        interval: function() {
          return 5000;
        }.property().readOnly()
      });
      this.set('pollster', p.create({
        onPoll: this.getStats,
        args: this.controllerFor('stats')
      }));
    }
    this.get('pollster').start();
  },
  deactivate: function() {
    this.get('pollster').stop();
  }
});
