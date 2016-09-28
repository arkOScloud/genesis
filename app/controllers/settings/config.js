import Ember from "ember";
import timezones from "../../utils/timezones";
import ENV from "../../config/environment";


export default Ember.ObjectController.extend({
  breadCrumb: {name: 'Preferences', icon: 'sliders'},
  timezones: timezones,
  config: {},
  hostname: "",
  tzRegion: "",
  tzZone: "",
  tzRegions: function() {
    return timezones.map(function(value) {
      return value.region;
    });
  }.property(),
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
  changeTzZone: function() {
    if (this.get('tzZones').indexOf(this.get('tzZone')) === -1) {
      this.set("tzZone", this.get('tzZones')[0]);
    }
  }.observes('tzZones'),
  offset: function() {
    if (this.get('model').datetime.datetime.offset !== "UNKNOWN") {
      return this.get('model').datetime.datetime.offset.toFixed(2);
    } else {
      return null;
    }
  }.property('model.datetime'),
  actions: {
    save: function() {
      var self = this;
      Ember.$.ajax(`${ENV.APP.krakenHost}/api/config`, {
        type: 'PUT',
        data: JSON.stringify({config: self.get('config'), hostname: self.get('hostname'),
            timezone: {region: self.get('tzRegion'), zone: self.get('tzZone').replace(" ", "_")}}),
        contentType: 'application/json',
        error: function(e) {
          if (e.status === 500) {
            self.transitionToRoute("error", e);
          } else if (e.errors) {
            e.errors.forEach(function(err) {
              self.notifications.new('error', err.detail);
            });
          }
        }
      });
    },
    openModal: function(name) {
      Ember.$('.ui.' + name + '.modal').modal('show');
    },
    addSSH: function() {
      var self = this;
      var key = this.store.createRecord('sshKey', {
        user: this.get('sshKeyUser'),
        key: this.get('sshKeyData')
      });
      var promise = key.save();
      promise.then(function(){
        self.setProperties({sshKeyUser: '', sshKeyData: ''});
      }, function(e){
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        } else if (e.errors) {
          e.errors.forEach(function(err) {
            self.notifications.new('error', err.detail);
          });
        }
        key.deleteRecord();
      });
    },
    clearModal: function() {
      this.setProperties({sshKeyUser: '', sshKeyData: ''});
    }
  }
});
