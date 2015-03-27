import Ember from "ember";
import ENV from "../config/environment";


export default Ember.Route.extend({
  model: function() {
    return Ember.RSVP.hash({
      certs: this.get('store').find('cert'),
      auths: this.get('store').find('certauth'),
      assns: $.getJSON(ENV.APP.krakenHost+'/certassigns')
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
