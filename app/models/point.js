import DS from "ember-data";


export default DS.Model.extend({
    icon: DS.attr('string'),
    type: DS.attr('string'),
    path: DS.attr('string')
});
