import Ember from 'ember';
import handleModelError from '../../../utils/handle-model-error';
import cardColor from '../../../utils/card-color';


export default Ember.Controller.extend({
  breadCrumb: {name: 'New database', icon: 'database'},
  cardColor: function() {
    return cardColor();
  }.property(),
  fields: {
    name: ['empty']
  },
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
        handleModelError(self, e);
        db.deleteRecord();
      });
    },
    redirect: function() {
      this.setProperties({id: '', dbType: this.get('dbTypes.firstObject')});
      this.transitionToRoute('tools.databases');
    }
  }
});
