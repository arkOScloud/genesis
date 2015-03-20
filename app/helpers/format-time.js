import Ember from "ember";
import ENV from "../config/environment";


export default Ember.Handlebars.makeBoundHelper(function(date){
  return new Ember.Handlebars.SafeString(moment(date).format(ENV.APP.timeFormat));
});
