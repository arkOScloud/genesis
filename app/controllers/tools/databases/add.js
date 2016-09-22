import Ember from 'ember';
import cardColor from '../../../utils/card-color';


export default Ember.Controller.extend({
  breadCrumb: {name: 'New database', icon: 'fa-database'},
  cardColor: function() {
    return cardColor();
  }.property(),
  actions: {
    save: function(){
      var self = this;
      var db = this.store.createRecord('database', {
        id: this.get('id'),
        databaseType: this.get('dbType') || this.get('dbTypes.firstObject')
      });
      var promise = db.save();
      promise.then(function(){
        self.setProperties({id: '', dbType: self.get('dbTypes.firstObject')});
        self.transitionToRoute("tools.databases");
      }, function(e){
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        }
        db.deleteRecord();
      });
    },
    redirect: function() {
      this.setProperties({id: '', dbType: this.get('dbTypes.firstObject')});
      this.transitionToRoute('tools.databases');
    }
  }
});
