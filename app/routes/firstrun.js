import Ember from "ember";
import ENV from "../config/environment";
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  beforeModel() {
    this.transitionTo('firstrun.start');
  },
  actions: {
    startSetup: function() {
      var self = this;
      var fin = this.controllerFor("firstrun.finish");
      var con = this.controllerFor("firstrun.confirm");
      fin.set("operations", {
        user: false,
        domain: false,
        timezone: false,
        firstrun: false,
        protectRoot: false,
        resizeSDCard: !(!!con.get("settings.resizeSDCard")),
        useGPUMem: !(!!con.get("settings.useGPUMem")),
        cubieMAC: !(!!con.get("settings.cubieMAC"))
      });
      this.transitionTo("firstrun.finish");
      var domain = this.store.createRecord('domain', {
        id: con.get('user.newDomain')
      });
      var pdom = domain.save();
      pdom.then(function(dom){
        fin.set("operations.domain", true);
        var user = self.store.createRecord('user', {
          name: con.get('user.newUser.name'),
          firstName: con.get('user.newUser.firstName'),
          lastName: con.get('user.newUser.lastName'),
          admin: true,
          sudo: true,
          domain: dom,
          passwd: con.get('user.newUser.passwd')
        });
        var pusr = user.save();
        pusr.then(function(){
          fin.set("operations.user", true);
          fin.set("canFinish", true);
        });
      });
      Ember.$.ajax(`${ENV.APP.krakenHost}/api/config`, {
        type: 'PUT',
        data: JSON.stringify({timezone: {region: con.get('settings.tzRegion'), zone: con.get('settings.tzZone').replace(" ", "_")}}),
        contentType: 'application/json',
        success: function() {
          fin.set("operations.timezone", true);
        }
      });
      var toInstall = [];
      con.get("apps.selectedApps").forEach(function(i) {
        toInstall.push(i.get("id"));
      });
      if (con.get("settings.resizeSDCard") || con.get("settings.useGPUMem") || con.get("settings.cubieMAC")) {
        fin.set("needsRestart", true);
      }
      Ember.$.ajax(`${ENV.APP.krakenHost}/api/firstrun`, {
        type: 'POST',
        data: JSON.stringify({
          install: toInstall,
          resize_sd_card: con.get("settings.resizeSDCard") || false,
          use_gpu_mem: con.get("settings.useGPUMem") || false,
          cubie_mac: con.get("settings.cubieMAC") || false,
          protectRoot: con.get("settings.protectRoot") || false
        }),
        contentType: 'application/json',
        success: function(j) {
          fin.set("operations.resizeSDCard", true);
          fin.set("operations.useGPUMem", true);
          fin.set("operations.cubieMAC", true);
          fin.set("operations.protectRoot", !!j.rootpwd || false);
          fin.set("rootPwd", j.rootpwd);
        }
      });
      Ember.$.ajax(`${ENV.APP.krakenHost}/api/config`, {
        type: 'PATCH',
        data: JSON.stringify({config: {genesis: {firstrun: true}}}),
        contentType: 'application/json'
      });
    },
    finish: function() {
      var self = this;
      ENV.APP.needsFirstRun = false;
      Ember.$.ajax(`${ENV.APP.krakenHost}/api/config`, {
        type: 'PATCH',
        data: JSON.stringify({config: {genesis: {anonymous: false, firstrun: true}}}),
        contentType: 'application/json',
        success: function() {
          self.transitionTo("login");
        }
      });
    }
  }
});
