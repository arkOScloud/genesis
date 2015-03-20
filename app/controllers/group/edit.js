import Ember from "ember";


export default Ember.ObjectController.extend({
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
