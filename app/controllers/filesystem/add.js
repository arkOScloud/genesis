import Ember from "ember";


export default Ember.ObjectController.extend({
  newFs: {},
  actions: {
    save: function(){
      var self = this;
      var fs = self.store.createRecord('filesystem', {
        id: self.get('newFs').name,
        size: parseInt(self.get('newFs').size)*1024*1024,
        crypt: self.get('newFs').crypt || false,
        passwd: self.get('newFs').passwd,
        isReady: false
      });
      var promise = fs.save();
      promise.then(function(){}, function(){
        fs.deleteRecord();
      });
    },
    removeModal: function(){
      this.set('newFs', {});
      return true;
    }
  }
});
