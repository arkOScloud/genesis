import Ember from "ember";
import ENV from "../config/environment";
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  model: function() {
    return Ember.RSVP.hash({
      sites: this.get('store').findAll('website'),
      users: this.get('store').findAll('user'),
      domains: this.get('store').findAll('domain'),
      dbType: this.get('store').findAll('databaseType'),
      apps: this.get('store').query('app', {type: "website", loadable: true})
    });
  },
  actions: {
    delete: function(model){
      model.set('isReady', false);
      Ember.$.ajax({
        url: ENV.APP.krakenHost+'/api/websites/'+model.get('id'),
        type: 'DELETE'
      });
    }
  }
});
