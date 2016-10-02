import Ember from 'ember';

export default Ember.Controller.extend({
  applicationController: Ember.inject.controller('application'),
  currentRouteName: Ember.computed.alias('applicationController.currentRouteName'),

  navName: function() {
    switch(this.get('currentRouteName')) {
      case 'tools.shares.shares.index':
        return 'Share';
      case 'tools.shares.mounts.index':
        return 'Mount';
      default:
        return '';
    }
  }.property('currentRouteName'),
  navIcon: function() {
    switch(this.get('currentRouteName')) {
      case 'tools.shares.shares.index':
        return 'external share';
      case 'tools.shares.mounts.index':
        return 'folder';
      default:
        return '';
    }
  }.property('currentRouteName'),
  navLink: function() {
    switch(this.get('currentRouteName')) {
      case 'tools.shares.shares.index':
        return 'tools.shares.shares.add';
      case 'tools.shares.mounts.index':
        return 'tools.shares.mounts.add';
      default:
        return '';
    }
  }.property('currentRouteName')
});
