import ApplicationSerializer from "./application";


export default ApplicationSerializer.extend({
  serialize: function(record, options) {
    var json = this._super(record, options);
    if (json) {
      json.type = record.get("typeId") || "";
    }
    return json;
  }
});
