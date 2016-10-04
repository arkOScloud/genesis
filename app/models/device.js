import DS from "ember-data";
import cardColor from "../utils/card-color";


export default DS.Model.extend({
    name: DS.attr('string'),
    deviceID: DS.attr('string'),
    certName: DS.attr('string'),
    compression: DS.attr('string'),
    introducer: DS.attr('boolean'),
    addresses: DS.attr(),
    isMainDevice: DS.attr('boolean'),
    selectId: function() {
      return this.get('deviceID');
    }.property('deviceID'),
    selectText: function() {
      return this.get('name');
    }.property('name'),
    cardColor: function() {
      return cardColor();
    }.property(),
    isReady: DS.attr('boolean')
});
