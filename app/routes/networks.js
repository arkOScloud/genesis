import Ember from "ember";
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  model: function() {
    return Ember.RSVP.hash({
      networks: this.get('store').findAll('network'),
      netifaces: this.get('store').findAll('netiface')
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
