import Ember from "ember";


export default Ember.ObjectController.extend({
  sortBy: ['id'],
  installedQuery: '',
  availableQuery: '',
  sortedPackages: Ember.computed.sort('model', 'sortBy'),
  installed: function() {
    return this.get('sortedPackages').filterBy('installed', true);
  }.property('sortedPackages'),
  upgradable: function() {
    return this.get('sortedPackages').filterBy('isUpgradable', true);
  }.property('sortedPackages'),
  filteredInstalled: Ember.computed.filter('installed', function(i) {
    return i.get('id').indexOf(this.get('installedQuery'))>=0;
  }).property('installed', 'installedQuery'),
  filteredAvailable: [],
  pendingOperations: function() {
    return this.get('model').filter(function(i) {
      return i.get('operation') !== "";
    });
  }.property('model.@each.operation'),
  actions: {
    showInfo: function(pkg) {
      pkg.reload();
      this.send('showModal', 'package/edit', pkg);
    },
    clearInstalledFilter: function() {
      this.set('installedQuery', '');
    },
    clearAvailableFilter: function() {
      this.set('availableQuery', '');
      this.set('filteredAvailable', []);
    },
    filterAvailable: function() {
      if (this.get('availableQuery') === '') {
        this.set('filteredAvailable', []);
        return false;
      }
      var self = this;
      this.set('filteredAvailable', this.get('sortedPackages').filter(function(i){
        return (i.get('installed') === false && i.get('id').indexOf(self.get('availableQuery'))>=0);
      }));
    },
    install: function(pkg) {
      if (pkg.get('operation') !== 'install') {
        pkg.set('operation', 'install');
        this.message.success(pkg.get('id')+' marked for install. Click Apply Changes to complete.');
      } else {
        pkg.rollback();
      }
    },
    remove: function(pkg) {
      if (pkg.get('operation') !== 'remove') {
        pkg.set('operation', 'remove');
        this.message.success(pkg.get('id')+' marked for removal. Click Apply Changes to complete.');
      } else {
        pkg.rollback();
      }
    },
    upgradeAll: function() {
      this.get('upgradable').forEach(function(i) {
        i.set('operation', 'install');
      });
      this.message.success('Packages marked for upgrade. Click Apply Changes to complete.');
    }
  }
});
