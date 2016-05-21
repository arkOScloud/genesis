import DS from "ember-data";


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
    addr: DS.attr('string'),
    port: DS.attr('number'),
    siteType: DS.attr('string'),
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
    hasActions: DS.attr('boolean', {defaultValue: false}),
    isReady: DS.attr('boolean', {defaultValue: false}),
    address: function() {
      var proto = this.get('certificate')?"https://":"http://",
          addr  = this.get('addr'),
          port  = [80, 443].indexOf(this.get('port'))>=0?"":":"+String(this.get('port'));
      return proto+addr+port;
    }.property('certificate', 'addr', 'port')
});
