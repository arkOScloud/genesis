import Ember from 'ember';
import cardColor from '../../../utils/card-color';


export default Ember.Controller.extend({
  breadCrumb: {name: 'New domain', icon: 'fa-code'},
  cardColor: cardColor(),
  actions: {
    save: function(){
      var self = this;
      if (this.store.hasRecordForId('domain', this.get('name'))) {
        this.message.danger('This domain already exists');
        return false;
      }
      var domain = this.store.createRecord('domain', {
        id: this.get('name'),
        cardColor: this.get('cardColor')
      });
      var promise = domain.save();
      promise.then(function(){}, function(e){
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        }
        domain.deleteRecord();
      });
    }
  }
});
