import Ember from 'ember';
import NotificationsInitializer from '../../../initializers/notifications';
import { module, test } from 'qunit';

let application;

module('Unit | Initializer | notifications', {
  beforeEach() {
    Ember.run(function() {
      application = Ember.Application.create();
      application.deferReadiness();
    });
  }
});

// Replace this with your real tests.
test('it works', function(assert) {
  NotificationsInitializer.initialize(application);

  // you would normally confirm the results of the initializer here
  assert.ok(true);
});
