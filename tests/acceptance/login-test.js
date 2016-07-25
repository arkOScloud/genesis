//login-test.js
import Ember from 'ember';
import startApp from '../helpers/start-app';

import {
	  module,
	  test,
	  visit,
	  andThen,
	  currentURL
	} from 'qunit';

var App;
module("Acceptance: Login", {
  setup: function(){
    App = startApp();
  },
  teardown: function(){
    Ember.run(App, 'destroy');
  }
});

test('visiting /login', function(assert) {
  visit('/login');

  andThen(function() {
    assert.equal(currentURL(), '/login');
  });
});
