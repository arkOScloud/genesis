/* global require, module */
var EmberApp = require('ember-cli/lib/broccoli/ember-app');
var Funnel = require('broccoli-funnel');

module.exports = function(defaults) {
  var app = new EmberApp(defaults, {
    'ember-cli-selectize': {
      'theme': 'bootstrap3'
    }
  });

  // Use `app.import` to add additional libraries to the generated
  // output files.
  //
  // If you need to use different assets in different
  // environments, specify an object as the first parameter. That
  // object's keys should be the environment name and the values
  // should be the asset to use in that environment.
  //
  // If the library that you are including contains AMD or ES6
  // modules that you would like to import into your application
  // please specify an object with the list of modules as keys
  // along with the exports of each module as its value.

  app.import('bower_components/moment/moment.js');
  app.import('bower_components/lightbox2/src/js/lightbox.js');
  app.import('bower_components/lightbox2/src/css/lightbox.css');
  app.import('bower_components/multiselect/js/jquery.multi-select.js');
  app.import('bower_components/multiselect/css/multi-select.css');
  app.import("bower_components/codemirror/lib/codemirror.css");
  app.import("bower_components/codemirror/lib/codemirror.js");
  app.import("bower_components/codemirror/mode/css/css.js");
  app.import("bower_components/codemirror/mode/htmlmixed/htmlmixed.js");
  app.import("bower_components/codemirror/mode/javascript/javascript.js");
  app.import("bower_components/codemirror/mode/markdown/markdown.js");
  app.import("bower_components/codemirror/mode/php/php.js");
  app.import("bower_components/codemirror/mode/python/python.js");
  app.import("bower_components/codemirror/mode/ruby/ruby.js");
  app.import("bower_components/codemirror/mode/shell/shell.js");
  app.import("bower_components/codemirror/mode/xml/xml.js");
  app.import("bower_components/font-awesome/css/font-awesome.css");
  app.import("bower_components/lato/css/lato.min.css");
  app.import("bower_components/fira/fira.css");
  var fontAwesome = new Funnel('bower_components/font-awesome/fonts', {
      srcDir: '/',
      destDir: 'fonts'
  });
  var firaEot = new Funnel('bower_components/fira/eot', {
      srcDir: '/',
      destDir: 'assets/eot'
  });
  var firaOtf = new Funnel('bower_components/fira/otf', {
      srcDir: '/',
      destDir: 'assets/otf'
  });
  var firaTtf = new Funnel('bower_components/fira/ttf', {
      srcDir: '/',
      destDir: 'assets/ttf'
  });
  var firaWoff = new Funnel('bower_components/fira/woff', {
      srcDir: '/',
      destDir: 'assets/woff'
  });
  var latoLight = new Funnel('bower_components/lato/font/lato-light', {
      srcDir: '/',
      destDir: 'assets/lato-light'
  });
  var latoThin = new Funnel('bower_components/lato/font/lato-thin', {
      srcDir: '/',
      destDir: 'assets/lato-thin'
  });
  var latoRegular = new Funnel('bower_components/lato/font/lato-regular', {
      srcDir: '/',
      destDir: 'assets/lato-regular'
  });
  var latoBold = new Funnel('bower_components/lato/font/lato-bold', {
      srcDir: '/',
      destDir: 'assets/lato-bold'
  });
  var latoItalic = new Funnel('bower_components/lato/font/lato-italic', {
      srcDir: '/',
      destDir: 'assets/lato-italic'
  });
  app.import("bower_components/lightbox2/src/images/close.png", {destDir: '/img'});
  app.import("bower_components/lightbox2/src/images/next.png", {destDir: '/img'});
  app.import("bower_components/lightbox2/src/images/prev.png", {destDir: '/img'});
  app.import("bower_components/lightbox2/src/images/loading.gif", {destDir: '/img'});
  app.import("bower_components/multiselect/img/switch.png", {destDir: '/img'});
  app.import('bower_components/bootstrap/dist/js/bootstrap.js');
  app.import('bower_components/bootstrap/dist/css/bootstrap.css');
  app.import('bower_components/bootstrap/dist/css/bootstrap.css.map', {
    destDir: 'assets'
  });
  app.import('bower_components/bootstrap-contextmenu/bootstrap-contextmenu.js');

  return app.toTree([fontAwesome, firaEot, firaOtf, firaTtf, firaWoff, latoThin, latoLight, latoRegular, latoBold, latoItalic]);
};
