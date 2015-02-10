Genesis.Cert = DS.Model.extend({
    domain: DS.attr('string'),
    expiry: DS.attr('date'),
    keylength: DS.attr('number'),
    keytype: DS.attr('string'),
    md5: DS.attr('string'),
    sha1: DS.attr('string'),
    assign: DS.attr(),
    isReady: DS.attr('boolean', {defaultValue: false}),
    typeString: function() {
      return this.get('keylength')+'-bit '+this.get('keytype');
    }.property('keylength', 'keytype')
});

Genesis.Certauth = DS.Model.extend({
    expiry: DS.attr('date'),
    downloadHref: function() {
      return Genesis.Config.krakenHost+'/certauths/'+this.get('id')+'?download=true';
    }.property('id')
});
