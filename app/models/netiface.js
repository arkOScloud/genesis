import DS from "ember-data";


export default DS.Model.extend({
    ip: DS.attr(),
    rx: DS.attr('number'),
    tx: DS.attr('number'),
    up: DS.attr('boolean'),
    type: DS.attr('string'),
    prettyType: function() {
      return `${this.get('type').capitalize()} (${this.get('id')})`;
    }.property('id', 'type')
});
