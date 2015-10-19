import Ember from "ember";
/* global moment */


export default Ember.Helper.helper(function(params){
  return new Ember.String.htmlSafe(moment(params[0]).fromNow());
});
