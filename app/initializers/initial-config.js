import Ember from "ember";
import ENV from "../config/environment";


export default {
  name: "initialConfig",
  initialize: function() {
    Ember.$.getJSON(`${ENV.APP.krakenHost}/api/config`, function(j){
      ENV.APP.dateFormat = j.config.general.date_format;
      ENV.APP.timeFormat = j.config.general.time_format;
      ENV.APP.needsFirstRun = !j.config.genesis.firstrun;
    });
  }
};
