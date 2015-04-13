import DS from "ember-data";


export default DS.Model.extend({
    name: DS.attr('string'),
    info: DS.attr('string'),
    date: DS.attr('date')
});
