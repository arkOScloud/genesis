import Ember from 'ember';
import AuthenticatedRouteMixin from 'simple-auth/mixins/authenticated-route-mixin';


export default Ember.Route.extend(AuthenticatedRouteMixin, {
  setupController: function(controller, model) {
    this._super(controller, model);
    var self = this;
    if (!this.get('isScheduled')) {
      Ember.run.later(this, function() {
        self.send('nextWelcome');
      }, 2000);
    }
  },
  actions: {
    nextWelcome: function() {
      var self = this,
          ctrl = this.controllerFor('firstrun.start');
      Ember.$('#welcome-text').transition('fade', function() {
        var currentIdx = ctrl.get('welcomes').indexOf(ctrl.get('welcome'));
        var nextIdx = (currentIdx === (ctrl.get('welcomes.length') - 1)) ? 0 : currentIdx + 1;
        ctrl.set('welcome', ctrl.get('welcomes').objectAt(nextIdx));
        Ember.$('#welcome-text').transition('fade');
        self.set('isScheduled', true);
        Ember.run.later(this, function() {
          self.send('nextWelcome');
        }, 3000);
      });
    }
  }
});
