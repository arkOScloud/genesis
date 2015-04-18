import ENV from "../config/environment";


export default {
  name: "initialConfig",
  initialize: function(container, application) {
    var initConfig = $.getJSON(ENV.APP.krakenHost+'/config', function(j){
      ENV.APP.dateFormat = j.config.general.date_format;
      ENV.APP.timeFormat = j.config.general.time_format;
      ENV.APP.needsFirstRun = !j.config.genesis.firstrun;
    });
  }
};
