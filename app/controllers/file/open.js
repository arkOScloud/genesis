import Ember from "ember";


export default Ember.ObjectController.extend({
  needs: ["files"],
  path: "",
  actions: {
    save: function(){
      this.get("controllers.files").openPath(this.get("path"));
    },
    removeModal: function(){
      this.set("path", "");
      return true;
    }
  }
});
