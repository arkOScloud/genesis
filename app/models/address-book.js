import DS from "ember-data";
import cardColor from "../utils/card-color";


export default DS.Model.extend({
    name: DS.attr('string'),
    filename: DS.attr('string'),
    user: DS.attr('string'),
    url: DS.attr('string'),
    isReady: DS.attr('boolean'),
    cardColor: function() {
      return cardColor();
    }.property()
});
