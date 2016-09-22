import Ember from "ember";


export default Ember.ObjectController.extend({
  needs: ['application'],
  breadCrumb: {name: 'Security', icon: 'fa-lock'},
  isFirewallPage: function() {
    return this.get('controllers.application.currentRouteName') === 'settings.security.firewall.index';
  }.property('controllers.application.currentRouteName')
});
