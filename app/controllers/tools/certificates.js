import Ember from 'ember';
import handleModelError from '../../utils/handle-model-error';


export default Ember.Controller.extend({
  queryParams: ['filter'],
  sortBy: ['id'],
  filter: 'certificates',
  breadCrumb: {name: 'Certificates', icon: 'certificate'},
  certificates: Ember.computed.sort('model.certs', 'sortBy'),
  authorities: Ember.computed.sort('model.auths', 'sortBy'),

  filteredCerts: Ember.computed('filter', 'sortedCerts', function() {
    var filter = this.get('filter');

    if (filter === 'certificates') {
      return this.get('certificates');
    } else if (filter === 'authorities') {
      return this.get('authorities');
    } else {
      return this.get('certificates');
    }
  }),

  certificatesFilter: function() {
    return this.get('filter') === 'certificates';
  }.property('filter'),
  authoritiesFilter: function() {
    return this.get('filter') === 'authorities';
  }.property('filter'),

  actions: {
    install: function(app) {
      var self = this;
      app.set('operation', 'install');
      app.set('isReady', false);
      var promise = app.save();
      promise.then(function(){}, function(e){
        handleModelError(self, e);
      });
    },
    setFilter: function(filt) {
      if (filt === 'authorities') {
        this.set('filter', 'authorities');
      } else {
        this.set('filter', 'certificates');
      }
    },
    openModal: function(name, cert) {
      this.set('selectedCert', cert);
      Ember.$('.ui.' + name + '.modal').modal('show');
    },
    deleteCert: function() {
      this.get('selectedCert').destroyRecord();
      this.set('selectedCert', null);
    },
    clearModal: function() {
      this.set('selectedCert', null);
    }
  }
});
