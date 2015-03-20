import DS from "ember-data";


export default DS.Model.extend({
    isReady: DS.attr('boolean', {defaultValue: false})
});
