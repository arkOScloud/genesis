import Ember from "ember";
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  beforeModel: function() {
    this.get('store').unloadAll('filesystem');
  },
  model: function() {
    return this.get('store').findAll('filesystem');
  }
});
