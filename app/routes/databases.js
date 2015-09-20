import Ember from "ember";
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  beforeModel: function() {
    this.get('store').unloadAll('database');
    this.get('store').unloadAll('databaseUser');
  },
  afterModel: function(model) {
    var self = this;
    model.types.forEach(function(i) {
      if (!i.get('state')) {
        self.message.danger(i.get('name')+' is not running. Start it via the Services pane to see its databases and perform tasks.');
      }
    });
  },
  model: function() {
    return Ember.RSVP.hash({
      dbs: this.get('store').findAll('database'),
      users: this.get('store').findAll('databaseUser'),
      types: this.get('store').findAll('databaseType')
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
