import Ember from 'ember';

export default Ember.Controller.extend({
  selectedApps: Ember.computed.filterBy('model', 'firstrunSelected', true),
  actions: {
    selectApp: function(app) {
      app.toggleProperty('firstrunSelected');
    },
    selectAll: function() {
      this.get("model").filterBy('installed', false).setEach('firstrunSelected', true);
    },
    deselectAll: function() {
      this.get("model").setEach('firstrunSelected', false);
    }
  }
});
