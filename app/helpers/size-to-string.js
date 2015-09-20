import Ember from "ember";
import sizeToString from "../utils/size-to-string";


export default Ember.Helper.helper(function(params){
  return new Ember.String.htmlSafe(sizeToString(params[0]));
});
