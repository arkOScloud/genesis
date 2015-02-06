Genesis.DatabaseController = Ember.ObjectController.extend();

Genesis.DatabaseAddController = Ember.ObjectController.extend({
  name: '',
  actions: {
    save: function(){
      var db = this.store.createRecord('database', {
        name: this.get('name'),
        typeId: this.get('type'),
        typeName: this.get('type')
      });
      var promise = db.save();
      promise.then(function(){}, function(){
        db.deleteRecord();
      });
    },
    removeModal: function(){
      this.set('name', '');
      this.set('type', '');
      return true;
    }
  }
});

Genesis.DatabaseAddUserController = Ember.ObjectController.extend({
  name: '',
  userTypes: function(){
    return this.get('types').filterProperty('supportsUsers', true);
  }.property('types'),
  actions: {
    save: function(){
      var db = this.store.createRecord('databaseUser', {
        name: this.get('name'),
        typeId: this.get('type'),
        passwd: this.get('passwd')
      });
      var promise = db.save();
      promise.then(function(){}, function(){
        db.deleteRecord();
      });
    },
    removeModal: function(){
      this.set('name', '');
      this.set('type', '');
      this.set('passwd', '');
      this.set('passwdb', '');
      return true;
    }
  }
});

Genesis.DatabaseEditController = Ember.ObjectController.extend({
  actions: {
    execute: function(){
      var self = this;
      var exec = $.ajax({
        url: Genesis.Config.krakenHost+'/databases/'+this.get('model').get('id'),
        data: JSON.stringify({"database": {"execute": this.get('execInput')}}),
        type: 'PUT',
        contentType: 'application/json',
        processData: false,
        success: function(j){
          self.set('execOutput', j.database.result);
        }
      });
    },
    removeModal: function(){
      this.set('execInput', '');
      this.set('execOutput', '');
      return true;
    }
  }
});

Genesis.DatabaseEditUserController = Ember.ObjectController.extend({
  actionsToTake: ["No action", "Grant all permissions", "Revoke all permissions"],
  availableDbs: function(){
    return this.get('model').get('extra').dbs.filterProperty('typeId', this.get('model').get('typeId'));
  }.property('dbs'),
  actions: {
    save: function(){
      var self = this;
      if (this.get('action') == "Grant all permissions") {
        actionToTake = "grant"
      } else if (this.get('action') == "Revoke all permissions") {
        actionToTake = "revoke"
      } else {
        return false;
      };
      var exec = $.ajax({
        url: Genesis.Config.krakenHost+'/database_users/'+this.get('model').get('id'),
        data: JSON.stringify({"database_user": {"operation": actionToTake, "database": this.get('database')}}),
        type: 'PUT',
        contentType: 'application/json',
        processData: false
      });
    },
    removeModal: function(){
      this.set('action', '');
      this.set('database', '');
      return true;
    }
  }
});
