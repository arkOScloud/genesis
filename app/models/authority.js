import DS from "ember-data";
import ENV from "../config/environment";
import cardColor from "../utils/card-color";


export default DS.Model.extend({
    expiry: DS.attr('date'),
    keylength: DS.attr('number'),
    keytype: DS.attr('string'),
    md5: DS.attr('string'),
    sha1: DS.attr('string'),
    certType: function() {
      return 'authority';
    }.property(),
    isAuthority: function() {
      return this.get('certType') === 'authority';
    }.property('certType'),
    typeString: function() {
      return `${this.get('keylength')}-bit ${this.get('keytype')} Authority`;
    }.property('keylength', 'keytype'),
    downloadHref: function() {
      return `${ENV.APP.krakenHost}/api/authorities/${this.get('id')}?download=true`;
    }.property('id'),
    cardColor: function() {
      return cardColor();
    }.property(),
    isReady: function() {
      return true;
    }.property()
});
