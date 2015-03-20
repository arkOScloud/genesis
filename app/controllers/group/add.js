import Ember from "ember";


export default Ember.ObjectController.extend({
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
