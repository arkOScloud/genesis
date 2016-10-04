import Ember from 'ember';
import ENV from "../../../config/environment";
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  model: function() {
    return Ember.$.getJSON(`${ENV.APP.krakenHost}/api/apps/syncthing/config`);
  }
});
