import Ember from 'ember';
import timezones from "../../utils/timezones";


export default Ember.Controller.extend({
  timezones: timezones,
  protectRoot: true,
  tzRegion: "GMT",
  tzZone: "GMT",
  tzZones: function() {
    var self = this;
    var tzo = timezones.find(function(i) {
      return i.region.replace(" ", "_") === self.get('tzRegion');
    });
    if (tzo.region === "GMT" || tzo.region === "UTC") {
      return [tzo.region];
    } else {
      return tzo.zones;
    }
  }.property('tzRegion'),
  usesSDCard: function() {
    return ["Unknown", "General"].indexOf(this.get("model.config.enviro.board")) === -1;
  }.property("model"),
  isRPi: function() {
    return ["Raspberry Pi", "Raspberry Pi 2", "Raspberry Pi 3"].indexOf(this.get("model.config.enviro.board")) >= 0;
  }.property("model"),
  isCubie: function() {
    return ["Cubieboard", "Cubietruck"].indexOf(this.get("model.config.enviro.board")) >= 0;
  }.property("model")
});
