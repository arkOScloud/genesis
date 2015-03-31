import DS from "ember-data";
import ENV from "../config/environment";


export default DS.Model.extend({
    path: DS.attr('string'),
    fetchCount: DS.attr('number'),
    expires: DS.attr('boolean'),
    expiresAt: DS.attr('date'),
    url: function() {
      return ENV.APP.krakenHost+'/shared/'+this.get('id');
    }.property('id'),
});
