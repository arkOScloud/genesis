import Ember from "ember";
import ENV from "../config/environment";
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  model: function() {
    return this.get('store').find('app');
  },
  actions: {
    refresh: function() {
      var self = this;
      $.getJSON(ENV.APP.krakenHost+"/api/apps?rescan=true", function(j){
        self.refresh();
      });
    },
    uninstall: function(app) {
      app.set('operation', 'uninstall');
      app.set('isReady', false);
      app.save();
    }
  }
});
