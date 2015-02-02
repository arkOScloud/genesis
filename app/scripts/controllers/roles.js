Genesis.UserController = Ember.ObjectController.extend();

Genesis.UserAddController = Ember.ObjectController.extend({
  newUser: {},
  actions: {
    save: function(){
      var self = this;
      $.getJSON(Genesis.Config.krakenHost+'/system/users/nextid', function(j){
        var user = self.store.createRecord('user', {
          id: j.uid,
          name: self.get('newUser').name,
          firstName: self.get('newUser').firstName,
          lastName: self.get('newUser').lastName,
          admin: self.get('newUser').admin || false,
          sudo: self.get('newUser').sudo || false,
          domain: self.get('newUser').domain,
          passwd: self.get('newUser').passwd
        });
        user.set('isPending', true);
        var promise = user.save();
        promise.then(function(){
            user.set('isPending', false);
          }, function(){
            user.deleteRecord();
        });
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
      user.set('isPending', true);
      var promise = user.save();
      promise.then(function(){
          user.set('isPending', false);
        }, function(){
          user.set('isPending', false);
      });
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
      $.getJSON(Genesis.Config.krakenHost+'/system/groups/nextid', function(j){
        var group = self.store.createRecord('group', {
          id: j.gid,
          name: self.get('name'),
          users: self.get('usersSelected')
        });
        group.set('isPending', true);
        var promise = group.save();
        promise.then(function(){
            group.set('isPending', false);
          }, function(){
            group.deleteRecord();
        });
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
      group.set('isPending', true);
      var promise = group.save();
      promise.then(function(){
          group.set('isPending', false);
        }, function(){
          group.set('isPending', false);
      });
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
      var domain = this.store.createRecord('domain', {
        id: this.get('name')
      });
      domain.set('isPending', true);
      var promise = domain.save();
      promise.then(function(){
          domain.set('isPending', false);
        }, function(){
          domain.deleteRecord();
      });
    },
    removeModal: function(){
      this.set('name', '');
      return true;
    }
  }
});
