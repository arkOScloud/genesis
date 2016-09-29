import Ember from "ember";


export default Ember.ObjectController.extend({
  applicationController: Ember.inject.controller('application'),
  breadCrumb: {name: 'Security', icon: 'shield'},
  isFirewallPage: function() {
    return this.get('applicationController.currentRouteName') === 'system.security.firewall.index';
  }.property('applicationController.currentRouteName')
});
