import Ember from 'ember';
import cardColor from '../../../utils/card-color';


export default Ember.Controller.extend({
  breadCrumb: {name: 'New database', icon: 'fa-database'},
  name: '',
  cardColor: cardColor(),
  actions: {
    save: function(){
      var self = this;
      var db = this.store.createRecord('database', {
        id: this.get('name'),
        typeId: this.get('type.id')
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
