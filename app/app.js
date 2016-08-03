import Ember from 'ember';
import Resolver from 'ember-resolver';
import loadInitializers from 'ember/load-initializers';
import config from './config/environment';

let App;

Ember.MODEL_FACTORY_INJECTIONS = true;

App = Ember.Application.extend({
  modulePrefix: config.modulePrefix,
  podModulePrefix: config.podModulePrefix,
  Resolver
});

loadInitializers(App, config.modulePrefix);

window.addEventListener("keydown", function(e){
  window.CTRL = (e.ctrlKey || e.metaKey);
}, false);

window.addEventListener('keyup', function(e){
  window.CTRL = (e.metaKey || e.ctrlKey);
}, false);

export default App;
