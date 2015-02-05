Genesis.CertController = Ember.ObjectController.extend();

Genesis.CertAddController = Ember.ObjectController.extend({
  newCert: {keylength: "2048"},
  keytypes: ["RSA", "DSA"],
  actions: {
    save: function(){
      var cert = this.store.createRecord('cert', {
        id: this.get('newCert').id,
        country: this.get('newCert').country,
        state: this.get('newCert').state,
        locale: this.get('newCert').locality,
        domain: this.get('newCert').domain,
        email: this.get('newCert').email,
        keytype: this.get('newCert').keytype,
        keylength: this.get('newCert').keylength,
        operation: 'generate'
      });
      var promise = cert.save();
      promise.then(function(){}, function(){
        cert.deleteRecord();
      });
    },
    removeModal: function(){
      this.set('newCert', {keylength: "2048"});
      return true;
    }
  }
});

Genesis.CertInfoController = Ember.ObjectController.extend();

Genesis.CertUploadController = Ember.ObjectController.extend({
  newCert: {},
  actions: {
    save: function(){
      var uploader = EmberUploader.Uploader.create({
        url: Genesis.Config.krakenHost+'/certs'
      });
      var files = [$('input[name="cert"]')[0].files[0],
                   $('input[name="key"]')[0].files[0]];
      if ($('input[name="chain"]')[0].files.length) {
        files.push($('input[name="chain"]')[0].files[0]);
      };
      uploader.upload(files, {id: this.get('name')});
    },
    removeModal: function(){
      this.set('name', '');
      return true;
    }
  }
});
