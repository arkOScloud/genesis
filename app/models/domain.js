import DS from "ember-data";
import cardColor from "../utils/card-color";


export default DS.Model.extend({
    isReady: DS.attr('boolean', {defaultValue: false}),
    cardColor: function() {
      return cardColor();
    }.property()
});
