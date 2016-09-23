import Ember from "ember";
import ENV from "../../config/environment";
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  model: function() {
    return Ember.RSVP.hash({
      backups: this.get('store').findAll('backup'),
      types: Ember.$.getJSON(ENV.APP.krakenHost+'/api/backups/types').then(function(j){return j.types;})
    });
  },
  actions: {
    restore: function(model){
      model.set('isReady', false);
      model.save();
    },
    delete: function(model){
      model.destroyRecord().then(function(){}, function(){
        model.rollback();
      });
    }
  }
});
