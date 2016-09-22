import Ember from "ember";


export default Ember.Controller.extend({
  userId: function() {
    if (this.get("session.isAuthenticated") && this.get("session.content.secure") && this.get("session.content.secure.token")) {
      var data = JSON.parse(atob(this.get("session.content.secure.token").split(".")[1]));
      return data.uln?(data.ufn+" "+data.uln):data.ufn;
    } else {
      return "Unknown User";
    }
  }.property("session.isAuthenticated"),
  showBreadCrumbs: function() {
    return ["login", "index"].indexOf(this.get("currentRouteName")) === -1;
  }.property("currentRouteName"),
  actions: {
    openModal: function(name) {
      Ember.$('.ui.' + name + '.modal').modal('show');
    }
  }
});
