import Ember from "ember";
import ENV from "../../config/environment";
import handleModelError from '../../utils/handle-model-error';


export default Ember.Controller.extend({
  breadCrumb: {name: 'Calendar/Contacts', icon: 'calendar'},
  setupPort: 80,
  fields: {
    port: ['integer', 'empty']
  },
  actions: {
    setup: function() {
      var self   = this;
      Ember.$.ajax(`${ENV.APP.krakenHost}/api/apps/radicale/setup`, {
        type: "POST",
        data: JSON.stringify(
          {
            config: {
              addr: this.get('setupDomain.id') || this.get('model.domains.firstObject.id'),
              port: this.get('setupPort')
            }
          }
        ),
        contentType: 'application/json'
      })
        .done(function() {
          self.set('model.status.installed', true);
          self.set('model.status.running', true);
        })
        .fail(function(e) {
          handleModelError(self, e);
        });
    },
    openModal: function(name, item) {
      this.set('selectedItem', item);
      Ember.$('.ui.' + name + '.modal').modal('show');
    },
    deleteItem: function() {
      this.get('selectedItem').destroyRecord();
      this.set('selectedItem', null);
    }
  }
});
