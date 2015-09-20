import Ember from "ember";
import ENV from "../config/environment";
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  model: function() {
    return this.get('store').findAll('app');
  },
  actions: {
    refresh: function() {
      var self = this;
      Ember.$.getJSON(ENV.APP.krakenHost+"/api/apps?rescan=true", function(){
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
