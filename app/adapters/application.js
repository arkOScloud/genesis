import Ember from "ember";
import DS from "ember-data";
import ENV from "../config/environment";


export default DS.RESTAdapter.extend({
    host: ENV.APP.krakenHost || "",
    namespace: "api",
    pathForType: function(type) {
      var stype = this._super(type);
      return Ember.String.decamelize(stype);
    }
});
