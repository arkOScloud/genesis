import DS from "ember-data";
import cardColor from "../utils/card-color";


export default DS.Model.extend({
    icon: DS.attr('string'),
    app: DS.belongsTo('app', {async: true}),
    appName: DS.attr('string'),
    properName: function() {
      if (!!this.get('app') && this.get('app.type') !== 'website') {
        return this.get("appName");
      }
      return this.get("id");
    }.property('id', 'app'),
    path: DS.attr('string'),
    domain: DS.belongsTo('domain', {async: true}),
    port: DS.attr('number'),
    version: DS.attr('string'),
    certificate: DS.attr('string'),
    database: DS.attr('string'),
    php: DS.attr('boolean'),
    enabled: DS.attr('boolean'),
    extraData: DS.attr(),
    operation: DS.attr('string'),
    newName: DS.attr('string'),
    hasUpdate: DS.attr('boolean'),
    isReady: DS.attr('boolean', {defaultValue: false}),
    address: function() {
      var isHTTPS = !!this.get('certificate'),
          port  = [80, 443].indexOf(this.get('port'))>=0?"":`:${this.get('port')}`;
      return `http${isHTTPS ? 's' : ''}://${this.get('domain.id')}${port}`;
    }.property('certificate', 'domain', 'port'),
    cardColor: function() {
      return cardColor();
    }.property()
});
