Genesis.User = DS.Model.extend({
    name: DS.attr('string'),
    firstName: DS.attr('string'),
    lastName: DS.attr('string'),
    admin: DS.attr('boolean', {defaultValue: false}),
    sudo: DS.attr('boolean', {defaultValue: false}),
    domain: DS.attr('string'),
    passwd: DS.attr('string'),
    isReady: DS.attr('boolean', {defaultValue: false}),
    selectId: function() {
      return this.get('name');
    }.property('name'),
    selectText: function() {
      return this.get('name');
    }.property('name')
});

Genesis.Group = DS.Model.extend({
    name: DS.attr('string'),
    users: DS.attr(),
    isReady: DS.attr('boolean', {defaultValue: false})
});

Genesis.Domain = DS.Model.extend({
    isReady: DS.attr('boolean', {defaultValue: false})
});
