import DS from "ember-data";


export default DS.Model.extend({
    name: DS.attr('string'),
    state: DS.attr('boolean'),
    supportsUsers: DS.attr('boolean', {defaultValue: false})
});
