import Ember from "ember";


export default Ember.ObjectController.extend({
  sortBy: ['id:desc'],
  updates: Ember.computed.sort('model', 'sortBy')
});
