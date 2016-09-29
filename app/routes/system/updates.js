import Ember from "ember";
import ENV from "../../config/environment";
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  model: function() {
    return this.get('store').findAll('update');
  },
  actions: {
    check: function() {
      var self = this;
      Ember.$.getJSON(ENV.APP.krakenHost+"/api/updates?rescan=true", function(){
        self.refresh();
      });
    },
    install: function() {
      Ember.$.ajax({
        url: ENV.APP.krakenHost+"/api/updates",
        method: "POST"
      });
    }
  }
});
