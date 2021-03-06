import Ember from 'ember';
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  renderTemplate: function() {
    this.render('app.syncthing.folders.edit', { into: 'application' });
  },
  afterModel: function() {
    var me = this;
    var devicesPromise = this.store.findAll('device');

    devicesPromise.then(function(devices) {
      me.controllerFor('app.syncthing.folders.edit').set('devices', devices);
    });

    return devicesPromise;
  }
});
