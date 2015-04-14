import DS from "ember-data";


export default DS.Model.extend({
    user: DS.attr('string'),
    key: DS.attr('string'),
    keyId: function() {
      return this.get("key").split(" ")[2];
    }.property("key")
});
