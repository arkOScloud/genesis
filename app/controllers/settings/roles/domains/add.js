import Ember from 'ember';
import cardColor from '../../../../utils/card-color';


export default Ember.Controller.extend({
  breadCrumb: {name: 'New domain', icon: 'code'},
  cardColor: cardColor(),
  actions: {
    save: function(){
      var self = this;
      var domain = this.store.createRecord('domain', {
        id: this.get('name'),
        cardColor: this.get('cardColor')
      });
      var promise = domain.save();
      promise.then(function() {
        self.transitionToRoute("settings.roles.domains");
      }, function(e) {
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        } else if (e.errors) {
          e.errors.forEach(function(err) {
            self.notifications.new('error', err.detail);
          });
        }
        domain.deleteRecord();
      });
    },
    redirect: function() {
      this.set('name', '');
      this.transitionToRoute('settings.roles.domains');
    }
  }
});
