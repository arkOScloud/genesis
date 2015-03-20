import DS from "ember-data";


export default DS.Model.extend({
    running: DS.attr('boolean'),
    enabled: DS.attr('boolean'),
    state: DS.attr('string'),
    type: DS.attr('string'),
    displayType: function() {
      return this.get('type').capitalize();
    }.property('type'),
    canManage: function() {
      return ["arkos-redis", "kraken", "slapd"].indexOf(this.get('id'))==-1;
    }.property('id'),
    operation: DS.attr('string'),
    cfg: DS.attr(),
    isReady: DS.attr('boolean', {defaultValue: false})
});
