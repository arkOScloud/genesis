import Ember from "ember";


export default Ember.Route.extend({
  activate: function() {
    $('body').addClass('login-page');
  },
  deactivate: function() {
    $('body').removeClass('login-page');
  }
});
