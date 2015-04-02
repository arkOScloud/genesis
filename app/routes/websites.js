import Ember from "ember";
import ENV from "../config/environment";
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  model: function() {
    return Ember.RSVP.hash({
      sites: this.get('store').find('website'),
      domains: this.get('store').find('domain'),
      dbType: this.get('store').find('databaseType'),
      apps: this.get('store').find('app', {type: "website", loadable: true})
    });
  },
  actions: {
    delete: function(model){
      model.set('isReady', false);
      $.ajax({
        url: ENV.APP.krakenHost+'/websites/'+model.get('id'),
        type: 'DELETE'
      });
    }
  }
});
