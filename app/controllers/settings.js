import Ember from 'ember';

export default Ember.Controller.extend({
  breadCrumb: {name: 'Settings', icon: 'fa-cogs', linkable: false},
  breadCrumbPath: false
});
