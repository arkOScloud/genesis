import DS from "ember-data";
import ENV from "../config/environment";
import cardColor from "../utils/card-color";


export default DS.Model.extend({
  name: DS.attr('string'),
  path: DS.attr('string'),
  fetchCount: DS.attr('number'),
  expires: DS.attr('boolean'),
  expiresAt: DS.attr('date'),
  isReady: DS.attr('boolean'),
  url: function() {
    return `${ENV.APP.krakenHost}/shared/${this.get('id')}`;
  }.property('id'),
  cardColor: function() {
    return cardColor();
  }.property()
});
