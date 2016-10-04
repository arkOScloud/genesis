import DS from "ember-data";
import cardColor from "../utils/card-color";


export default DS.Model.extend({
  label: DS.attr('string'),
  type: DS.attr('string'),
  path: DS.attr('string'),
  order: DS.attr('string'),
  hashers: DS.attr('number'),
  invalid: DS.attr('string'),
  ignorePerms: DS.attr('boolean', {defaultValue: false}),
  devices: DS.attr(),
  isReadOnly: function() {
    return this.get('type') === 'readonly';
  }.property('type'),
  lenientMTimes: DS.attr('boolean', {defaultValue: false}),
  rescanIntervalS: DS.attr('number'),
  copiers: DS.attr('number'),
  autoNormalize: DS.attr('boolean', {defaultValue: false}),
  versioning: DS.attr(),
  hasVersioning: function() {
    return !!this.get('versioning.type');
  }.property('versioning'),
  pullers: DS.attr('number'),
  cardColor: function() {
    return cardColor();
  }.property(),
  isReady: DS.attr('boolean')
});
