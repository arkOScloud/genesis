import DS from "ember-data";
import cardColor from "../utils/card-color";


export default DS.Model.extend({
    name: DS.attr('string'),
    users: DS.attr(),
    isReady: DS.attr('boolean', {defaultValue: false}),
    cardColor: function() {
      return cardColor();
    }.property()
});
