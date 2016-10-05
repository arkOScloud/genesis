import Ember from 'ember';
import handleModelError from '../../../../utils/handle-model-error';
import cardColor from '../../../../utils/card-color';


export default Ember.Controller.extend({
  breadCrumb: {name: 'New domain', icon: 'code'},
  cardColor: cardColor(),
  fields: {
    domain: ['regExp[/^[a-zA-Z0-9-_\.]+$/]']
  },
  actions: {
    save: function(){
      var self = this;
      var domain = this.store.createRecord('domain', {
        id: this.get('name'),
        cardColor: this.get('cardColor')
      });
      var promise = domain.save();
      promise.then(function() {
        self.transitionToRoute("system.roles.domains");
      }, function(e) {
        handleModelError(self, e);
        domain.deleteRecord();
      });
    },
    redirect: function() {
      this.set('name', '');
      this.transitionToRoute('system.roles.domains');
    }
  }
});
