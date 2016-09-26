import Ember from 'ember';

export default Ember.Controller.extend({
  breadCrumb: {name: 'Networking', icon: 'sitemap'},
  queryParams: ['filter'],
  sortBy: ['id'],
  filter: null,
  sortedNetworks: Ember.computed.sort('model.networks', 'sortBy'),

  filteredNetworks: Ember.computed('filter', 'sortedNetworks', function() {
    var filter = this.get('filter');
    var networks = this.get('sortedNetworks');

    if (filter === 'wired') {
      return networks.filterBy('type', 'Ethernet');
    } else if (filter === 'wireless') {
      return networks.filterBy('type', 'Wireless');
    } else {
      return networks;
    }
  }),

  allFilter: function() {
    return this.get('filter') === null;
  }.property('filter'),
  wiredFilter: function() {
    return this.get('filter') === 'wired';
  }.property('filter'),
  wirelessFilter: function() {
    return this.get('filter') === 'wireless';
  }.property('filter'),

  actions: {
    setFilter: function(filt) {
      if (filt === 'wired') {
        this.set('filter', 'wired');
      } else if (filt === 'wireless') {
        this.set('filter', 'wireless');
      } else {
        this.set('filter', null);
      }
    },
    toggle: function(net) {
      var self = this;
      net.set('operation', net.get('connected')?'disconnect':'connect');
      net.set('isReady', false);
      var promise = net.save();
      promise.then(function(){}, function(e){
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        }
      });
    },
    toggleEnabled: function(net) {
      var self = this;
      net.set('operation', net.get('enabled')?'disable':'enable');
      net.set('isReady', false);
      var promise = net.save();
      promise.then(function(){}, function(e){
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        }
      });
    },
    openModal: function(name, net) {
      this.set('selectedNet', net);
      Ember.$('.ui.' + name + '.modal').modal('show');
    },
    deleteNet: function() {
      this.get('selectedNet').destroyRecord();
      this.set('selectedNet', null);
    },
    clearModal: function() {
      this.set('selectedNet', null);
    }
  }
});
