import Ember from "ember";


export default Ember.ObjectController.extend({
  breadCrumb: {name: 'Filesystems', icon: 'disk outline'},
  queryParams: ['filter'],
  filter: null,

  filteredFSes: Ember.computed('filter', 'sortedCerts', function() {
    var filter = this.get('filter');

    if (filter === 'virtual') {
      return this.get('model').filterBy('isVirtual', true);
    } else if (filter === 'physical') {
      return this.get('model').filterBy('isVirtual', false);
    } else {
      return this.get('model');
    }
  }),

  allFilter: function() {
    return !this.get('filter');
  }.property('filter'),
  virtualFilter: function() {
    return this.get('filter') === 'virtual';
  }.property('filter'),
  physicalFilter: function() {
    return this.get('filter') === 'physical';
  }.property('filter'),

  actions: {
    setFilter: function(filt) {
      if (filt === 'virtual') {
        this.set('filter', 'virtual');
      } else if (filt === 'physical') {
        this.set('filter', 'physical');
      } else {
        this.set('filter', null);
      }
    },
    mount: function(fs) {
      var self = this;
      fs.set('operation', 'mount');
      fs.set('isReady', false);
      var promise = fs.save();
      promise.then(function(){}, function(e){
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        } else if (e.errors) {
          e.errors.forEach(function(err) {
            self.notifications.new('error', err.detail);
          });
        }
      });
    },
    umount: function(fs){
      var self = this;
      fs.set('operation', 'umount');
      fs.set('isReady', false);
      var promise = fs.save();
      promise.then(function(){}, function(e){
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        } else if (e.errors) {
          e.errors.forEach(function(err) {
            self.notifications.new('error', err.detail);
          });
        }
      });
    },
    enable: function(fs) {
      var self = this;
      fs.set('operation', 'enable');
      fs.set('isReady', false);
      var promise = fs.save();
      promise.then(function(){}, function(e){
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        } else if (e.errors) {
          e.errors.forEach(function(err) {
            self.notifications.new('error', err.detail);
          });
        }
      });
    },
    disable: function(fs) {
      var self = this;
      fs.set('operation', 'disable');
      fs.set('isReady', false);
      var promise = fs.save();
      promise.then(function(){}, function(e){
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        } else if (e.errors) {
          e.errors.forEach(function(err) {
            self.notifications.new('error', err.detail);
          });
        }
      });
    },
    openModal: function(name, fs) {
      this.set('selectedFS', fs);
      Ember.$('.ui.' + name + '.modal').modal('show');
    },
    mountEnc: function() {
      var fs = this.get('selectedFS');
      var self = this;
      fs.set('operation', 'mount');
      fs.set('passwd', this.get('passwd'));
      fs.set('isReady', false);
      var promise = fs.save();
      promise.then(function(){}, function(e){
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        } else if (e.errors) {
          e.errors.forEach(function(err) {
            self.notifications.new('error', err.detail);
          });
        }
      });
      this.setProperties({selectedFS: null, passwd: null});
    },
    deleteFs: function() {
      var fs = this.get('selectedFS');
      fs.destroyRecord().then(function(){}, function(){
        fs.rollback();
      });
      this.setProperties({selectedFS: null, passwd: null});
    },
    clearModal: function() {
      this.setProperties({selectedFS: null, passwd: null});
    }
  }
});
