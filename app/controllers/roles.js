import Ember from 'ember';

export default Ember.Controller.extend({
  needs: ['application'],
  currentRouteName: Ember.computed.alias('controllers.application.currentRouteName'),

  navName: function() {
    switch(this.get('currentRouteName')) {
      case 'roles.users.index':
        return 'User';
      case 'roles.groups.index':
        return 'Group';
      case 'roles.domains.index':
        return 'Domain';
      default:
        return '';
    }
  }.property('currentRouteName'),
  navIcon: function() {
    switch(this.get('currentRouteName')) {
      case 'roles.users.index':
        return 'fa-user';
      case 'roles.groups.index':
        return 'fa-group';
      case 'roles.domains.index':
        return 'fa-code';
      default:
        return '';
    }
  }.property('currentRouteName'),
  navLink: function() {
    switch(this.get('currentRouteName')) {
      case 'roles.users.index':
        return 'roles.users.add';
      case 'roles.groups.index':
        return 'roles.groups.add';
      case 'roles.domains.index':
        return 'roles.domains.add';
      default:
        return '';
    }
  }.property('currentRouteName')
});
