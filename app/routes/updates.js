import Ember from "ember";
import ENV from "../config/environment";
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  model: function() {
    return this.get('store').find('update');
  },
  actions: {
    check: function() {
      var self = this;
      $.getJSON(ENV.APP.krakenHost+"/api/updates?rescan=true", function(j){
        self.refresh();
      });
    },
    install: function() {
      $.ajax({
        url: ENV.APP.krakenHost+"/api/updates",
        method: "POST"
      });
    }
  }
});
