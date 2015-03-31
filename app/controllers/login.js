import Ember from 'ember';
import LoginControllerMixin from 'simple-auth/mixins/login-controller-mixin';


export default Ember.Controller.extend(LoginControllerMixin, {
  authenticator: 'simple-auth-authenticator:jwt',
  loginMessage: "",
  actions: {
    authenticate: function() {
      this.set("loginMessage", "");
      this._super();
    }
  }
});
