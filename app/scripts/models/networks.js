Genesis.Network = DS.Model.extend({
    connected: DS.attr('boolean'),
    enabled: DS.attr('boolean'),
    config: DS.attr(),
    type: function() {
      return this.get('config').connection=="wireless"?"Wireless":"Ethernet";
    }.property('config'),
    typeIcon: function() {
      return this.get('config').connection=="wireless"?"fa-wifi":"fa-sitemap";
    }.property('config'),
    operation: DS.attr('string'),
    isReady: DS.attr('boolean', {defaultValue: false})
});

Genesis.Netiface = DS.Model.extend({
    ip: DS.attr(),
    rx: DS.attr('number'),
    tx: DS.attr('number'),
    up: DS.attr('boolean'),
    type: DS.attr('string'),
    prettyType: function() {
      return this.get('type').capitalize() + " ("+this.get('id')+")";
    }.property('id', 'type')
});
