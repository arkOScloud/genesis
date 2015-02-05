Genesis.CertSerializer = Genesis.ApplicationSerializer.extend({
  serialize: function(record, options) {
    var json = this._super(record, options);
    if (json) {
      json.country = record.get("country") || "";
      json.state = record.get("state") || "";
      json.locale = record.get("locale") || "";
      json.email = record.get("email") || "";
    }
    return json;
  }
});

Genesis.DatabaseSerializer = Genesis.ApplicationSerializer.extend({
  serialize: function(record, options) {
    var json = this._super(record, options);
    if (json) {
      json.type = record.get("typeId") || "";
    }
    return json;
  }
});

Genesis.DatabaseUserSerializer = Genesis.ApplicationSerializer.extend({
  serialize: function(record, options) {
    var json = this._super(record, options);
    if (json) {
      json.type = record.get("typeId") || "";
      json.passwd = record.get("passwd") || "";
    }
    return json;
  }
});
