Genesis.ApplicationSerializer = DS.RESTSerializer.extend({
  serializeIntoHash: function(data, type, record, options) {
    var root = Ember.String.decamelize(type.typeKey);
    data[root] = this.serialize(record, options);
  },
  keyForAttribute: function(attr) {
    return Ember.String.decamelize(attr);
  }
});
