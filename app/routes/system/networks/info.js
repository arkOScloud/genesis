import Ember from 'ember';
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  renderTemplate: function() {
    this.render('system.networks.info', { into: 'application' });
  },
  afterModel: function() {
    var me = this;
    var ifacesPromise = this.store.findAll('netiface');

    ifacesPromise.then(function(ifaces) {
      me.controllerFor('system.networks.info').set('netifaces', ifaces);
    });

    return ifacesPromise;
  }
});
