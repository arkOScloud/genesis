import Ember from "ember";


export default Ember.ObjectController.extend({
  actions: {
    mount: function(fs){
      var self = this;
      fs.set('operation', 'mount');
      fs.set('isReady', false);
      var promise = fs.save();
      promise.then(function(){}, function(e){
        if (e.status == 500) self.transitionToRoute("error", e);
      });
    },
    umount: function(fs){
      var self = this;
      fs.set('operation', 'umount');
      fs.set('isReady', false);
      var promise = fs.save();
      promise.then(function(){}, function(e){
        if (e.status == 500) self.transitionToRoute("error", e);
      });
    },
    enable: function(fs){
      var self = this;
      fs.set('operation', 'enable');
      fs.set('isReady', false);
      var promise = fs.save();
      promise.then(function(){}, function(e){
        if (e.status == 500) self.transitionToRoute("error", e);
      });
    },
    disable: function(fs){
      var self = this;
      fs.set('operation', 'disable');
      fs.set('isReady', false);
      var promise = fs.save();
      promise.then(function(){}, function(e){
        if (e.status == 500) self.transitionToRoute("error", e);
      });
    }
  }
});
