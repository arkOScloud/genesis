import Ember from "ember";


export default Ember.ObjectController.extend({
  actions: {
    mount: function(fs){
      fs.set('operation', 'mount');
      fs.set('isReady', false);
      fs.save();
    },
    umount: function(fs){
      fs.set('operation', 'umount');
      fs.set('isReady', false);
      fs.save();
    },
    enable: function(fs){
      fs.set('operation', 'enable');
      fs.set('isReady', false);
      fs.save();
    },
    disable: function(fs){
      fs.set('operation', 'disable');
      fs.set('isReady', false);
      fs.save();
    }
  }
});
