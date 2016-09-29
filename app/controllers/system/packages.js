import Ember from "ember";
import handleModelError from '../../utils/handle-model-error';
import ENV from "../../config/environment";


export default Ember.ObjectController.extend({
  breadCrumb: {name: 'Packages', icon: 'cube'},
  queryParams: ['filter'],
  filter: null,
  search: "",
  sortBy: ['id'],
  sortedPackages: Ember.computed.sort('model', 'sortBy'),
  filteredPackages: Ember.computed('filter', 'sortedPackages', function() {
    var filter = this.get('filter');
    if (["", null].indexOf(filter) !== -1) {
      return this.get('sortedPackages').filterBy('installed', true);
    } else if (filter === 'upgradable') {
      return this.get('sortedPackages').filterBy('isUpgradable', true);
    } else {
      return this.get('sortedPackages').filter(function(i) {
        return i.get('id').toLowerCase().indexOf(filter.toLowerCase()) >= 0;
      });
    }
  }),
  installedFilter: function() {
    return ["", null].indexOf(this.get('filter')) !== -1;
  }.property('filter'),
  upgradableFilter: function() {
    return this.get('filter') === 'upgradable';
  }.property('filter'),
  searchFilter: function() {
    return ["", null, 'upgradable'].indexOf(this.get('filter')) === -1;
  }.property('filter'),
  pendingOperations: function() {
    return this.get('model').filter(function(i) {
      return i.get('operation') !== "";
    });
  }.property('model.@each.operation'),

  actions: {
    getInfo: function(pkg) {
      pkg.reload();
      this.send('openModal', 'package-info', pkg);
    },
    install: function(pkg) {
      if (pkg.get('operation') !== 'install') {
        pkg.set('operation', 'install');
        this.notifications.new("success", pkg.get('id')+' marked for install. Click Apply Changes to complete.');
      } else {
        pkg.rollback();
      }
    },
    remove: function(pkg) {
      if (pkg.get('operation') !== 'remove') {
        pkg.set('operation', 'remove');
        this.notifications.new("success", pkg.get('id')+' marked for removal. Click Apply Changes to complete.');
      } else {
        pkg.rollback();
      }
    },
    upgradeAll: function() {
      this.get('model').filterBy('isUpgradable', true).setEach('operation', 'install');
      this.notifications.new("success", 'Packages marked for upgrade. Click Apply Changes to complete.');
    },
    beginOperations: function() {
      var self = this;
      var toSend = Ember.A();
      this.get('pendingOperations').forEach(function(i) {
        toSend.pushObject({id: i.get('id'), operation: i.get('operation')});
        i.set('operation', '');
      });
      Ember.$.ajax(`${ENV.APP.krakenHost}/api/system/packages`, {
        data: JSON.stringify({packages: toSend}),
        type: 'POST',
        contentType: 'application/json'
      })
        .error(function(e) {
          handleModelError(self, e);
        });
    },
    search: function(term) {
      this.set('filter', term);
    },
    clearOperations: function() {
      var self = this;
      Ember.$('.ui.package-ops.modal').modal('hide', function() {
        self.get('model').setEach('operation', '');
      });
    },
    clearSearch: function() {
      this.set('search', "");
      this.set('filter', null);
    },
    setFilter: function(filt) {
      if (filt === 'upgradable') {
        this.set('filter', 'upgradable');
      } else {
        this.set('filter', null);
      }
    },
    openModal: function(name, pack) {
      this.set('selectedPackage', pack);
      Ember.$('.ui.' + name + '.modal').modal('show');
    }
  }
});
