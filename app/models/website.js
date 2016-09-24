import DS from "ember-data";
import cardColor from "../utils/card-color";


export default DS.Model.extend({
    name: DS.attr('string'),
    properName: function() {
      if (this.get('siteType') === "internal") {
        return this.get("name");
      } else {
        return this.get("id");
      }
    }.property('id', 'name', 'siteType'),
    path: DS.attr('string'),
    domain: DS.belongsTo('domain', {async: true}),
    port: DS.attr('number'),
    siteType: DS.belongsTo('app', {async: true}),
    siteName: DS.attr('string'),
    siteIcon: DS.attr('string'),
    version: DS.attr('string'),
    certificate: DS.attr('string'),
    database: DS.attr('string'),
    php: DS.attr('boolean'),
    enabled: DS.attr('boolean'),
    extraData: DS.attr(),
    operation: DS.attr('string'),
    newName: DS.attr('string'),
    isReady: DS.attr('boolean', {defaultValue: false}),
    address: function() {
      var proto = this.get('certificate')?"https://":"http://",
          addr  = this.get('domain.id'),
          port  = [80, 443].indexOf(this.get('port'))>=0?"":":"+String(this.get('port'));
      return proto+addr+port;
    }.property('certificate', 'addr', 'port'),
    cardColor: function() {
      return cardColor();
    }.property()
});
