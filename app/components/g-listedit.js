import Ember from "ember";


export default Ember.Component.extend({
  newItem: "",
  actions: {
    addItem: function() {
      this.get("items").pushObject(this.get("newItem")+(this.get("suffix") || ""));
    },
    removeItem: function(item) {
      this.get("items").removeObject(item);
    }
  }
});
