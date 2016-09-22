import DS from "ember-data";
import cardColor from "../utils/card-color";


export default DS.Model.extend({
    connected: DS.attr('boolean'),
    enabled: DS.attr('boolean'),
    config: DS.attr(),
    type: function() {
      return this.get('config').connection === "wireless" ? "Wireless" : "Ethernet";
    }.property('config'),
    typeIcon: function() {
      return this.get('config').connection === "wireless" ? "wifi icon" : "sitemap icon";
    }.property('config'),
    cardColor: function() {
      return cardColor();
    }.property(),
    operation: DS.attr('string'),
    isReady: DS.attr('boolean', {defaultValue: false})
});
