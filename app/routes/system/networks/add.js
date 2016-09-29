import Ember from 'ember';
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  renderTemplate: function() {
    this.render('system.networks.add', { into: 'application' });
  },
  afterModel: function() {
    var me = this;
    var ifacesPromise = this.store.findAll('netiface');

    ifacesPromise.then(function(ifaces) {
      me.controllerFor('system.networks.add').set('netifaces', ifaces);
    });

    return ifacesPromise;
  }
});
