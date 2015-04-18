import DS from "ember-data";
import ENV from "../config/environment";


export default DS.Model.extend({
    size: DS.attr('number'),
    typeId: DS.attr('string'),
    typeName: DS.attr('string'),
    downloadHref: function() {
      return ENV.APP.krakenHost+'/api/databases/'+this.get('id')+'?download=true';
    }.property('id'),
    isReady: DS.attr('boolean', {defaultValue: false})
});
