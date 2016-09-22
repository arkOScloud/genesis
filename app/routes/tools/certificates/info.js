import Ember from 'ember';
import ENV from '../../../config/environment';
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  renderTemplate: function() {
    this.render('tools.certificates.info', { into: 'application' });
  },
  afterModel: function() {
    var me = this;
    var assignsPromise = Ember.$.getJSON(ENV.APP.krakenHost+'/api/assignments');

    assignsPromise.then(function(assigns) {
      me.controllerFor('tools.certificates.info').set('certAssigns', assigns.assignments);
    });

    return assignsPromise;
  }
});
