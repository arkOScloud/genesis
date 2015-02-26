Genesis.FilesystemController = Ember.ObjectController.extend();

Genesis.FilesystemsController = Ember.ObjectController.extend({
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
    }
  }
});

Genesis.FilesystemAddController = Ember.ObjectController.extend({
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

Genesis.FilesystemMntcryptController = Ember.ObjectController.extend({
  actions: {
    save: function() {
      var fs = this.get('model');
      fs.set('operation', 'mount');
      fs.set('isReady', false);
      fs.save();
    },
    removeModal: function(){
      this.get('model').setProperties({
        operation: '',
        passwd: ''
      });
      return true;
    }
  }
});
