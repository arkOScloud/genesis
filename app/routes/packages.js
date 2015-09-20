import Ember from "ember";
import ENV from "../config/environment";
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  model: function() {
    return this.get('store').findAll('package');
  },
  actions: {
    refresh: function() {
      var self = this;
      Ember.$.getJSON(ENV.APP.krakenHost+"/api/system/packages?refresh=true", function(){
        self.refresh();
      });
    }
  }
});
