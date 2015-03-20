import Ember from "ember";
import ENV from "../config/environment";


export default Ember.Controller.extend({
  currentVersion: ENV.APP.currentVersion
});
