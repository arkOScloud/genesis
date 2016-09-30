import Ember from 'ember';
import ENV from "../../../config/environment";
import EmberUploader from 'ember-uploader';
import handleModelError from '../../../utils/handle-model-error';


export default Ember.Controller.extend({
  breadCrumb: {name: 'New certificate', icon: 'certificate'},
  isACMESelected: true,
  keyTypes: ["RSA", "DSA"],
  keylength: 2048,
  fields: {
    name: ['regExp[/^[a-zA-Z0-9][a-zA-Z0-9-_]+$/]', 'maxLength[30]', 'empty'],
    country: ['maxLength[2]', 'regExp[/^[A-Z]+$/]', 'empty'],
    state: ['empty'],
    city: ['empty'],
    email: ['email', 'empty'],
    keylength: ['integer', 'empty']
  },
  actions: {
    selectType: function(t) {
      if (t === "ACME") {
        this.setProperties({
          isACMESelected: true,
          isSSCSelected: false,
          isUploadSelected: false
        });
      } else if (t === "SSC") {
        this.setProperties({
          isACMESelected: false,
          isSSCSelected: true,
          isUploadSelected: false
        });
      } else if (t === "Upload") {
        this.setProperties({
          isACMESelected: false,
          isSSCSelected: false,
          isUploadSelected: true
        });
      }
    },
    saveACME: function() {
      var self = this,
          domain = this.get('domain') || this.get('domains.firstObject');
      var cert = this.store.createRecord('certificate', {
        id: domain.get('id'),
        domain: domain,
        keytype: "RSA",
        keylength: 2048,
        isAcme: true
      });
      var promise = cert.save();
      promise.then(function(){
        self.transitionToRoute('tools.certificates');
      }, function(e){
        handleModelError(self, e);
        cert.deleteRecord();
      });
    },
    saveSSC: function() {
      var self = this,
          keytype = this.get('keytype') || this.get('keyTypes.firstObject'),
          domain = this.get('domain') || this.get('domains.firstObject');
      var cert = this.store.createRecord('certificate', {
        id: this.get('name'),
        country: this.get('country'),
        state: this.get('state'),
        locale: this.get('city'),
        domain: domain,
        email: this.get('email'),
        keytype: keytype,
        keylength: this.get('keylength')
      });
      var promise = cert.save();
      promise.then(function(){
        self.transitionToRoute('tools.certificates');
      }, function(e){
        handleModelError(self, e);
        cert.deleteRecord();
      });
    },
    saveUpload: function() {
      var self = this;
      var uploader = EmberUploader.Uploader.create({
        url: `${ENV.APP.krakenHost}/api/certificates`
      });
      var files = [Ember.$('input[name="cert"]')[0].files[0],
                   Ember.$('input[name="key"]')[0].files[0]];
      if (Ember.$('input[name="chain"]')[0].files.length) {
        files.push(Ember.$('input[name="chain"]')[0].files[0]);
      }
      var promise = uploader.upload(files, {id: this.get('name')});
      promise.then(function(){
        self.transitionToRoute('tools.certificates');
      }, function(e){
        handleModelError(self, e);
      });
    },
    redirect: function() {
      this.transitionToRoute('tools.certificates');
    }
  }
});
