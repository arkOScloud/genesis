import Ember from "ember";
import ENV from "../config/environment";
/* global moment */


export default Ember.Helper.helper(function(params){
  return new Ember.String.htmlSafe(moment(params[0]).format(ENV.APP.timeFormat));
});
