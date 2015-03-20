import Ember from "ember";


export default Ember.ObjectController.extend({
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
