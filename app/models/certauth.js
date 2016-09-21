import DS from "ember-data";
import ENV from "../config/environment";
import cardColor from "../utils/card-color";


export default DS.Model.extend({
    expiry: DS.attr('date'),
    certType: function() {
      return 'authority';
    }.property(),
    isAuthority: function() {
      return this.get('certType') === 'authority';
    }.property('certType'),
    typeString: function() {
      return this.get('keylength')+'-bit '+this.get('keytype');
    }.property('keylength', 'keytype'),
    downloadHref: function() {
      return ENV.APP.krakenHost+'/api/certauths/'+this.get('id')+'?download=true';
    }.property('id'),
    cardColor: function() {
      return cardColor();
    }.property(),
    isReady: function() {
      return true;
    }.property()
});
