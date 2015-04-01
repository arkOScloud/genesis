import Ember from "ember";
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  model: function() {
    return this.get('store').find('app');
  },
  actions: {
    uninstall: function(app) {
      app.set('operation', 'uninstall');
      app.set('isReady', false);
      app.save();
    }
  }
});
