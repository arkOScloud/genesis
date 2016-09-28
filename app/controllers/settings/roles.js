import Ember from 'ember';

export default Ember.Controller.extend({
  applicationController: Ember.inject.controller('application'),
  currentRouteName: Ember.computed.alias('applicationController.currentRouteName'),

  navName: function() {
    switch(this.get('currentRouteName')) {
      case 'settings.roles.users.index':
        return 'User';
      case 'settings.roles.groups.index':
        return 'Group';
      case 'settings.roles.domains.index':
        return 'Domain';
      default:
        return '';
    }
  }.property('currentRouteName'),
  navIcon: function() {
    switch(this.get('currentRouteName')) {
      case 'settings.roles.users.index':
        return 'user';
      case 'settings.roles.groups.index':
        return 'group';
      case 'settings.roles.domains.index':
        return 'code';
      default:
        return '';
    }
  }.property('currentRouteName'),
  navLink: function() {
    switch(this.get('currentRouteName')) {
      case 'settings.roles.users.index':
        return 'settings.roles.users.add';
      case 'settings.roles.groups.index':
        return 'settings.roles.groups.add';
      case 'settings.roles.domains.index':
        return 'settings.roles.domains.add';
      default:
        return '';
    }
  }.property('currentRouteName')
});
