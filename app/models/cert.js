import DS from "ember-data";


export default DS.Model.extend({
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
