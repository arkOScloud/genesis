import Ember from 'ember';

export default Ember.Controller.extend({
  user: Ember.inject.controller('firstrun.user'),
  settings: Ember.inject.controller('firstrun.settings'),
  apps: Ember.inject.controller('firstrun.apps'),
  operations: {},
  rootPwd: "Please wait..."
});
