import Ember from "ember";


export default Ember.Route.extend({
  model: function() {
    return this.get('store').find('app');
  },
  actions: {
    uninstall: function(app) {
      app.set('operation', 'uninstall');
      app.set('isReady', false);
      app.save();
    }
  }
});
