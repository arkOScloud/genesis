import Ember from 'ember';

export default Ember.Controller.extend({
  applicationController: Ember.inject.controller('application'),
  currentRouteName: Ember.computed.alias('applicationController.currentRouteName'),

  navName: function() {
    switch(this.get('currentRouteName')) {
      case 'system.roles.users.index':
        return 'User';
      case 'system.roles.groups.index':
        return 'Group';
      case 'system.roles.domains.index':
        return 'Domain';
      default:
        return '';
    }
  }.property('currentRouteName'),
  navIcon: function() {
    switch(this.get('currentRouteName')) {
      case 'system.roles.users.index':
        return 'user';
      case 'system.roles.groups.index':
        return 'group';
      case 'system.roles.domains.index':
        return 'code';
      default:
        return '';
    }
  }.property('currentRouteName'),
  navLink: function() {
    switch(this.get('currentRouteName')) {
      case 'system.roles.users.index':
        return 'system.roles.users.add';
      case 'system.roles.groups.index':
        return 'system.roles.groups.add';
      case 'system.roles.domains.index':
        return 'system.roles.domains.add';
      default:
        return '';
    }
  }.property('currentRouteName')
});
