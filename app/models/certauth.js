import DS from "ember-data";
import ENV from "../config/environment";


export default DS.Model.extend({
    expiry: DS.attr('date'),
    downloadHref: function() {
      return ENV.APP.krakenHost+'/api/certauths/'+this.get('id')+'?download=true';
    }.property('id')
});
