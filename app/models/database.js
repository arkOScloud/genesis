import DS from "ember-data";
import ENV from "../config/environment";
import cardColor from "../utils/card-color";


export default DS.Model.extend({
    size: DS.attr('number'),
    databaseType: DS.belongsTo('database-type'),
    downloadHref: function() {
      return `${ENV.APP.krakenHost}/api/databases/${this.get('id')}?download=true`;
    }.property('id'),
    isReady: DS.attr('boolean', {defaultValue: false}),
    cardColor: function() {
      return cardColor();
    }.property()
});
