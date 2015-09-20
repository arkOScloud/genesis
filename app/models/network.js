import DS from "ember-data";


export default DS.Model.extend({
    connected: DS.attr('boolean'),
    enabled: DS.attr('boolean'),
    config: DS.attr(),
    type: function() {
      return this.get('config').connection === "wireless" ? "Wireless" : "Ethernet";
    }.property('config'),
    typeIcon: function() {
      return this.get('config').connection === "wireless" ? "fa-wifi" : "fa-sitemap";
    }.property('config'),
    operation: DS.attr('string'),
    isReady: DS.attr('boolean', {defaultValue: false})
});
