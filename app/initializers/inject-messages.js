export default {
  name: "injectMessages",
  initialize: function(container, application) {
    application.inject('controller', 'message', 'message:main');
    application.inject('component',  'message', 'message:main');
    application.inject('adapter',    'message', 'message:main');
    application.inject('route',      'message', 'message:main');
  }
};
