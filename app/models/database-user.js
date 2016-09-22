import DS from "ember-data";
import cardColor from "../utils/card-color";


export default DS.Model.extend({
    typeId: DS.attr('string'),
    typeName: DS.attr('string'),
    permissions: DS.attr('string'),
    isReady: DS.attr('boolean', {defaultValue: false}),
    cardColor: function() {
      return cardColor();
    }.property()
});
