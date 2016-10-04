import Ember from "ember";
import handleModelError from '../../../utils/handle-model-error';
import cardColor from '../../../utils/card-color';


export default Ember.Controller.extend({
  breadCrumb: {name: 'New address book', icon: 'book'},
  fields: {
    name: ['empty']
  },
  cardColor: function() {
    return cardColor();
  }.property(),
  actions: {
    save: function() {
      var self = this,
          user = this.get('user.name') || self.get('model.firstObject.name');
      var book = self.store.createRecord('addressBook', {
        id: user+"_"+self.get('name'),
        name: self.get('name'),
        user: user
      });
      var promise = book.save();
      promise.then(function() {
        self.transitionToRoute('app.radicale');
      }, function(e){
        handleModelError(self, e);
        book.deleteRecord();
      });
    }
  },
  redirect: function() {
    this.transitionToRoute('app.radicale');
  }
});
