import Ember from "ember";


export default Ember.ObjectController.extend({
  assignsSelected: [],
  assignsSelectedProp: (function(){
    this.get('model.assignsSelected');
  }).property("assignsSelected.@each"),
  actions: {
    addSelected: (function(id){
      this.get("assignsSelected").pushObject(id[0]);
    }),
    removeSelected: (function(id){
      this.get("assignsSelected").removeObject(id[0]);
    }),
    save: function(){
      var self    = this,
          cert    = this.get('model'),
          avail   = this.get('model.extra.assns.certassigns'),
          assigns = [];
      this.get('assignsSelected').forEach(function(i){
        assigns.pushObject(avail.filterBy('id', i)[0]);
      });
      cert.set('assigns', assigns);
      cert.set('isReady', false);
      var promise = cert.save();
      promise.then(function(){}, function(e){
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        }
      });
    },
    removeModal: function(){
      if (this.get('model').get('isDirty')) {
        this.get('model').rollback();
      }
      this.set("assignsSelected", []);
      return true;
    }
  }
});
