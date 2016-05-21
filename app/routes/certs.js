import Ember from "ember";
import ENV from "../config/environment";
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  model: function() {
    return Ember.RSVP.hash({
      certs: this.get('store').findAll('cert'),
      auths: this.get('store').findAll('certauth'),
      assns: Ember.$.getJSON(ENV.APP.krakenHost+'/api/certassigns')
    });
  },
  actions: {
    delete: function(model){
      model.destroyRecord().then(function(){}, function(){
        model.rollback();
      });
    }
  }
});
