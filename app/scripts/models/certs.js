Genesis.Cert = DS.Model.extend({
    domain: DS.attr('string'),
    expiry: DS.attr('date'),
    keylength: DS.attr('number'),
    keytype: DS.attr('string'),
    md5: DS.attr('string'),
    sha1: DS.attr('string'),
    assign: DS.attr(),
    isReady: DS.attr('boolean', {defaultValue: false})
});

Genesis.Certauth = DS.Model.extend({
    expiry: DS.attr('date')
});
