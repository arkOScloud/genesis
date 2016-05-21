import Ember from "ember";


export default Ember.ObjectController.extend({
  newCert: {keylength: "2048"},
  keytypes: ["RSA", "DSA"],
  actions: {
    save: function(){
      var self = this;
      var cert = this.store.createRecord('cert', {
        id: this.get('newCert').id,
        country: this.get('newCert').country,
        state: this.get('newCert').state,
        locale: this.get('newCert').locality,
        domain: this.get('newCert').domain,
        email: this.get('newCert').email,
        keytype: this.get('newCert').keytype,
        keylength: this.get('newCert').keylength
      });
      var promise = cert.save();
      promise.then(function(){}, function(e){
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        }
        cert.deleteRecord();
      });
    },
    removeModal: function(){
      this.set('newCert', {keylength: "2048"});
      return true;
    }
  }
});
