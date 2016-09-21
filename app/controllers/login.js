import Ember from 'ember';


export default Ember.Controller.extend({
  loginMessage: "",
  actions: {
    authenticate: function() {
      var credentials = this.getProperties('identification', 'password'),
        authenticator = 'simple-auth-authenticator:jwt';
      this.controllerFor("login").set("isLoading", true);
      this.set("loginMessage", "");
      this.get('session').authenticate(authenticator, credentials);
    }
  }
});
