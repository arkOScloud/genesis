import DS from 'ember-data';
import cardColor from "../utils/card-color";


export default DS.Model.extend({
  name: DS.attr('string'),
  icon: DS.attr('string'),
  supportsValidUsers: function() {
    return this.get('id') !== 'fs-nfs';
  }.property('id'),
  supportsComments: function() {
    return this.get('id') === 'fs-samba';
  }.property('id'),
  supportsMounts: function() {
    return this.get('id') !== 'fs-afp';
  }.property('id'),
  cardColor: function() {
    return cardColor();
  }.property()
});
