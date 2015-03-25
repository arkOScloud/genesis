import Ember from "ember";
import ENV from "../config/environment";
import Router from "../router";


export default {
  name: "registerAppRoutes",
  initialize: function(container, application) {
    application.deferReadiness();
    $.getJSON(ENV.APP.krakenHost+'/apps', function(m){
      m.apps.forEach(function(i){
        if (i.type=='app' && i.installed) {
          Router.map(function(){
            this.route(i.id);
          });
        };
      });
      application.advanceReadiness();
    });
  }
};
