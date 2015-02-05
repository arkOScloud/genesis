Genesis.Database = DS.Model.extend({
    name: DS.attr('string'),
    size: DS.attr('string'),
    typeId: DS.attr('string'),
    typeName: DS.attr('string'),
    isReady: DS.attr('boolean', {defaultValue: false})
});

Genesis.DatabaseUser = DS.Model.extend({
    name: DS.attr('string'),
    typeId: DS.attr('string'),
    typeName: DS.attr('string'),
    permissions: DS.attr('string'),
    isReady: DS.attr('boolean', {defaultValue: false})
});

Genesis.DatabaseType = DS.Model.extend({
    name: DS.attr('string'),
    supportsUsers: DS.attr('boolean', {defaultValue: false})
});
