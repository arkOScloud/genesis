import DS from 'ember-data';
import cardColor from "../utils/card-color";


export default DS.Model.extend({
  shareType: DS.belongsTo('share-type', {async: true}),
  path: DS.attr('string'),
  networkPath: DS.attr('string'),
  isMounted: DS.attr('boolean'),
  readOnly: DS.attr('boolean'),
  username: DS.attr('string'),
  password: DS.attr('string'),
  isReady: DS.attr('boolean'),
  cardColor: function() {
    return cardColor();
  }.property()
});
