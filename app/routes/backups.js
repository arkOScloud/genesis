import Ember from "ember";
import ENV from "../config/environment";


export default Ember.Route.extend({
  model: function() {
    return Ember.RSVP.hash({
      backups: this.get('store').find('backup'),
      types: $.getJSON(ENV.APP.krakenHost+'/backups/types').then(function(j){return j.types;})
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
