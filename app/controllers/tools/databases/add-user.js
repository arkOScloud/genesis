import Ember from 'ember';
import cardColor from '../../../utils/card-color';


export default Ember.Controller.extend({
  breadCrumb: {name: 'New user', icon: 'fa-user'},
  name: '',
  cardColor: cardColor(),
  userTypes: function(){
    return this.get('types').filterProperty('supportsUsers', true);
  }.property('types'),
  actions: {
    save: function(){
      var self = this;
      var db = this.store.createRecord('databaseUser', {
        id: this.get('id'),
        typeId: this.get('type.id'),
        passwd: this.get('passwd')
      });
      var promise = db.save();
      promise.then(function(){
        self.transitionToRoute("tools.databases");
      }, function(e){
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        }
        db.deleteRecord();
      });
    }
  }
});
