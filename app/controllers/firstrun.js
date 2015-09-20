import Ember from "ember";
import ENV from "../config/environment";
import timezones from "../utils/timezones";


export default Ember.ObjectController.extend({
  timezones: timezones,
  operations: {},
  newUser: {},
  newDomain: "arkos.local",
  tzRegion: "GMT",
  tzZone: "GMT",
  rootPwd: "Please wait...",
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
  canFinish: false,
  usesSDCard: function() {
    return ["Unknown", "General"].indexOf(this.get("model.config").config.enviro.board) === -1;
  }.property("model.config"),
  isRPi: function() {
    return ["Raspberry Pi", "Raspberry Pi 2"].indexOf(this.get("model.config").config.enviro.board) >= 0;
  }.property("model.config"),
  isCubie: function() {
    return ["Cubieboard", "Cubietruck"].indexOf(this.get("model.config").config.enviro.board) >= 0;
  }.property("model.config"),
  actions: {
    selectApp: function(app) {
      if (app.get("firstrunSelected")) {
        app.set("firstrunSelected", false);
      } else {
        app.set("firstrunSelected", true);
      }
    },
    selectAll: function() {
      this.get("model.apps").forEach(function(i) {
        i.set("firstrunSelected", true);
      });
    },
    deselectAll: function() {
      this.get("model.apps").forEach(function(i) {
        i.set("firstrunSelected", false);
      });
    },
    startSetup: function() {
      var self = this;
      this.set("operations", {
        user: false,
        domain: false,
        timezone: false,
        firstrun: false,
        resizeSDCard: !(!!this.get("resizeSDCard")),
        useGPUMem: !(!!this.get("useGPUMem")),
        cubieMAC: !(!!this.get("cubieMAC"))
      });
      this.send("nextStep");
      var domain = this.store.createRecord('domain', {
        id: this.get('newDomain')
      });
      var pdom = domain.save();
      pdom.then(function(){
        self.set("operations.domain", true);
        var user = self.store.createRecord('user', {
          name: self.get('newUser').name,
          firstName: self.get('newUser').firstName,
          lastName: self.get('newUser').lastName,
          admin: true,
          sudo: true,
          domain: self.get('newDomain'),
          passwd: self.get('newUser').passwd
        });
        var pusr = user.save();
        pusr.then(function(){
          self.set("operations.user", true);
          self.set("canFinish", true);
        });
      });
      Ember.$.ajax({
        url: ENV.APP.krakenHost+'/api/config',
        type: 'PUT',
        data: JSON.stringify({timezone: {region: self.get('tzRegion'), zone: self.get('tzZone').replace(" ", "_")}}),
        contentType: 'application/json',
        processData: false,
        success: function() {
          self.set("operations.timezone", true);
        }
      });
      var toInstall = [];
      this.get("model.apps").filterBy("firstrunSelected").forEach(function(i) {
        toInstall.push(i.get("id"));
      });
      if (this.get("resizeSDCard") || this.get("useGPUMem") || this.get("cubieMAC")) {
        self.set("needsRestart", true);
      }
      Ember.$.ajax({
        url: ENV.APP.krakenHost+'/api/firstrun',
        type: 'POST',
        data: JSON.stringify({
          install: toInstall,
          resize_sd_card: self.get("resizeSDCard") || false,
          use_gpu_mem: self.get("useGPUMem") || false,
          cubie_mac: self.get("cubieMAC") || false
        }),
        contentType: 'application/json',
        processData: false,
        success: function(j) {
          self.set("operations.resizeSDCard", true);
          self.set("operations.useGPUMem", true);
          self.set("operations.cubieMAC", true);
          self.set("rootPwd", j.rootpwd);
        }
      });
      Ember.$.ajax({
        url: ENV.APP.krakenHost+'/api/config',
        type: 'PATCH',
        data: JSON.stringify({config: {genesis: {firstrun: true}}}),
        contentType: 'application/json',
        processData: false
      });
    }
  }
});
