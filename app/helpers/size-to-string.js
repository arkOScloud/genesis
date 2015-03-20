import Ember from "ember";
import sizeToString from "../utils/size-to-string";


export default Ember.Handlebars.makeBoundHelper(function(size){
  return new Ember.Handlebars.SafeString(sizeToString(size));
});
