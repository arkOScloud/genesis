import DS from "ember-data";


export default DS.Model.extend({
    typeId: DS.attr('string'),
    typeName: DS.attr('string'),
    permissions: DS.attr('string'),
    isReady: DS.attr('boolean', {defaultValue: false})
});
