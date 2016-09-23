import Ember from "ember";
import ENV from "../../config/environment";
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  model: function() {
    return Ember.RSVP.hash({
      shares: this.get('store').findAll('share'),
      POIs: this.get('store').findAll('point')
    });
  },
  setupController: function(controller, model) {
    this._super();
    controller.set('model', model);
    if (!this.get("currentPath")) {
        this.set('currentPath', "/");
        Ember.$.getJSON(`${ENV.APP.krakenHost}/api/files/Lw**`)
          .done(function(j) {
            controller.set('currentFolder', j.files);
          });
    }
  }
});
