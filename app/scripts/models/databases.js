Genesis.Database = DS.Model.extend({
    size: DS.attr('string'),
    typeId: DS.attr('string'),
    typeName: DS.attr('string'),
    downloadHref: function() {
      return Genesis.Config.krakenHost+'/databases/'+this.get('id')+'?download=true';
    }.property('id'),
    isReady: DS.attr('boolean', {defaultValue: false})
});

Genesis.DatabaseUser = DS.Model.extend({
    typeId: DS.attr('string'),
    typeName: DS.attr('string'),
    permissions: DS.attr('string'),
    isReady: DS.attr('boolean', {defaultValue: false})
});

Genesis.DatabaseType = DS.Model.extend({
    name: DS.attr('string'),
    state: DS.attr('boolean'),
    supportsUsers: DS.attr('boolean', {defaultValue: false})
});
