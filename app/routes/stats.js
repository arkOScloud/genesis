import Ember from "ember";
import ENV from "../config/environment";
import Pollster from "../objects/pollster";


export default Ember.Route.extend({
  getStats: function() {
    $.getJSON(ENV.APP.krakenHost+'/system/stats/all').then(function(j) {
      var cpu = Math.round(j.cpu);
      $('#cpu .progress-bar').css('width', cpu+'%').attr('aria-valuenow', cpu);
      $('#cpu .progress-bar').html(cpu+'%');
      $('#cpu .text-center').remove();
      $('#memory .progress-bar').css('width', j.ram[2]+'%').attr('aria-valuenow', j.ram[2]);
      $('#memory .progress-bar').html(j.ram[2]+'%');
      $('#memory .text-center').html(Math.round(j.ram[0]/1024/1024)+' Mb used of '+Math.round(j.ram[1]/1024/1024)+' Mb available');
      var swap = Math.round(j.swap[1]/j.swap[0] || 0);
      $('#swap .progress-bar').css('width', swap+'%').attr('aria-valuenow', swap);
      $('#swap .progress-bar').html(swap+'%');
      $('#swap .text-center').html(Math.round(j.swap[0]/1024/1024)+' Mb used of '+Math.round(j.swap[1]/1024/1024)+' Mb available');
      $('#load .text-center').removeClass('text-center').addClass('load-text');
      $('#load .load-text').html('<span class="text-muted">1 min:</span> '+j.load[0]+'<span class="text-muted">, 5 min:</span> '+j.load[1]+'<span class="text-muted">, 15 min:</span> '+j.load[2])
      $('#temp .text-center').html(j.temp || "Unavailable");
      $('#uptime .text-center').html(j.uptime);
    });
  },
  setupController: function() {
    this.getStats();
    if (Ember.isNone(this.get('pollster'))) {
      var p = Pollster.extend({
        interval: function() {
          return 5000;
        }.property().readOnly()
      });
      this.set('pollster', p.create({
        onPoll: this.getStats
      }));
    }
    this.get('pollster').start();
  },
  deactivate: function() {
    this.get('pollster').stop();
  }
});
