import Ember from "ember";
import DS from "ember-data";


export default DS.RESTSerializer.extend({
  serializeIntoHash: function(data, type, record, options) {
    var root = Ember.String.decamelize(type.typeKey);
    data[root] = this.serialize(record, options);
  },
  keyForAttribute: function(attr) {
    return Ember.String.decamelize(attr);
  },
  keyForRelationship: function(name) {
    return Ember.String.decamelize(name);
  }
});
