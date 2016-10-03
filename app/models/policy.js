import DS from "ember-data";
import cardColor from "../utils/card-color";


export default DS.Model.extend({
    name: DS.attr('string'),
    icon: DS.attr('string'),
    policy: DS.attr('number'),
    ports: DS.attr(),
    type: DS.attr('string'),
    cardColor: function() {
      return cardColor();
    }.property(),
    displayPorts: function() {
      var portsStrings = [];
      this.get('ports').forEach(function(i) {
        portsStrings.push(i[1]+" ("+i[0]+")");
      });
      return portsStrings.join(", ");
    }.property('ports'),
    policyDisplayIcon: function() {
      var policy = this.get('policy');
      if (policy === 0) {
        return "minus circle";
      } else if (policy === 1) {
        return "home";
      } else if (policy === 2) {
        return "check circle";
      } else {
        return "";
      }
    }.property('policy'),
    policyDisplayText: function() {
      var policy = this.get('policy');
      if (policy === 0) {
        return "Deny All Connections";
      } else if (policy === 1) {
        return "Local Networks Only";
      } else if (policy === 2) {
        return "Allow All Connections";
      } else {
        return "Unknown Policy";
      }
    }.property('policy'),
    policyDisplayClass: function() {
      var policy = this.get('policy');
      if (policy === 0) {
        return "text red";
      } else if (policy === 2) {
        return "text green";
      } else {
        return "text black";
      }
    }.property('policy'),
    notWideOpen: function() {
      return this.get('policy') !== 2;
    }.property('policy'),
    notLocal: function() {
      return this.get('policy') !== 1;
    }.property('policy'),
    notDenied: function() {
      return this.get('policy') !== 0;
    }.property('policy'),
    canDeny: function() {
      return this.get('type') !== "arkos";
    }.property('type'),
    isCustomPolicy: function() {
      return this.get('type') === "custom";
    }.property('type'),
    isReady: DS.attr('boolean', {defaultValue: false})
});
