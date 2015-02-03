Genesis.UserController = Ember.ObjectController.extend();

Genesis.UserAddController = Ember.ObjectController.extend({
  newUser: {},
  actions: {
    save: function(){
      var self = this;
      var user = self.store.createRecord('user', {
        name: self.get('newUser').name,
        firstName: self.get('newUser').firstName,
        lastName: self.get('newUser').lastName,
        admin: self.get('newUser').admin || false,
        sudo: self.get('newUser').sudo || false,
        domain: self.get('newUser').domain,
        passwd: self.get('newUser').passwd
      });
      var promise = user.save();
      promise.then(function(){}, function(){
        user.deleteRecord();
      });
    },
    removeModal: function(){
      this.set('newUser', {});
      return true;
    }
  }
});

Genesis.UserEditController = Ember.ObjectController.extend({
  needs: 'user',
  actions: {
    save: function(){
      var user = this.get('model');
      user.set('isReady', false);
      var promise = user.save();
    },
    removeModal: function(){
      var user = this.get('model');
      user.setProperties({
        "passwd": "",
        "passwdb": ""
      });
      return true;
    }
  }
});

Genesis.GroupController = Ember.ObjectController.extend();

Genesis.GroupAddController = Ember.ObjectController.extend({
  name: "",
  usersSelected: [],
  usersSelectedProp: (function(){
    this.get("usersSelected");
  }).property("usersSelected.@each"),
  actions: {
    addSelectedId: (function(id){
      this.get("usersSelected").pushObject(id[0]);
    }),
    removeSelectedId: (function(id){
      this.get("usersSelected").removeObject(id[0]);
    }),
    save: function(){
      var self = this;
      var group = self.store.createRecord('group', {
        name: self.get('name'),
        users: self.get('usersSelected')
      });
      var promise = group.save();
      promise.then(function(){}, function(){
        group.deleteRecord();
      });
    },
    removeModal: function(){
      this.setProperties({
        "user": "",
        "usersSelected": []
      });
      return true;
    }
  }
});

Genesis.GroupEditController = Ember.ObjectController.extend({
  needs: 'group',
  usersSelected: [],
  usersSelectedProp: (function(){
    this.get('model').get("usersSelected");
  }).property("usersSelected.@each"),
  actions: {
    addSelectedId: (function(id){
      this.get("usersSelected").pushObject(id[0]);
    }),
    removeSelectedId: (function(id){
      this.get("usersSelected").removeObject(id[0]);
    }),
    save: function(){
      var group = this.get('model');
      group.set('users', this.get("usersSelected"));
      group.set('isReady', false);
      var promise = group.save();
    },
    removeModal: function(){
      if (this.get('model').get('isDirty')) {
        this.get('model').rollback();
      };
      this.set("usersSelected", []);
      return true;
    }
  }
});

Genesis.DomainController = Ember.ObjectController.extend();

Genesis.DomainAddController = Ember.ObjectController.extend({
  needs: 'domain',
  actions: {
    save: function(){
      if (this.store.hasRecordForId('domain', this.get('name'))) {
        Genesis.addMessage('error', 'This domain already exists');
        return false;
      };
      var domain = this.store.createRecord('domain', {
        id: this.get('name')
      });
      var promise = domain.save();
      promise.then(function(){}, function(){
        domain.deleteRecord();
      });
    },
    removeModal: function(){
      this.set('name', '');
      return true;
    }
  }
});
