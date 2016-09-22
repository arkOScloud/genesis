import Ember from 'ember';

export default Ember.Controller.extend({
  breadCrumb: {name: 'Statistics', icon: 'fa-area-chart'},
  cpuPct: 0,
  memory: 0,
  memoryPct: 0,
  memoryTotal: 0,
  swap: 0,
  swapPct: 0,
  swapTotal: 0,
  load1min: 0,
  load5min: 0,
  load10min: 0,
  temp: 0,
  uptimeDays: 0,
  uptimeHours: 0,
  uptimeMinutes:0,
  uptimeSeconds: 0
});
