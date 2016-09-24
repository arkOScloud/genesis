import DS from "ember-data";
import cardColor from "../utils/card-color";


export default DS.Model.extend({
    pid: DS.attr('string'),
    type: DS.attr('string'),
    siteType: DS.attr('string'),
    icon: DS.attr('string'),
    version: DS.attr('string'),
    path: DS.attr('string'),
    time: DS.attr('date'),
    size: DS.attr('number'),
    isReady: DS.attr('boolean', {defaultValue: false}),
    cardColor: function() {
      return cardColor();
    }.property()
});
