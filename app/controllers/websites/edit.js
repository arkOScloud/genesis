import Ember from 'ember';
import handleModelError from '../../utils/handle-model-error';
import ENV from '../../config/environment';


export default Ember.Controller.extend({
  breadCrumb: Ember.computed("model.properName", "model.icon", {
    get() {
      return {name: this.get("model.properName"), icon: this.get("model.icon")};
    }
  }),
  newName: function() {
    return this.get('model').get('id');
  }.property('model'),
  fields: {
    name: {
      rules: [
        {
          type: 'regExp[/^[a-zA-Z0-9_]+$/]',
          prompt: 'Site name must be included and not include dashes, spaces or special characters'
        }
      ]
    },
    port: {
      rules: [
        {
          type: 'integer[1..65536]'
        }
      ]
    }
  },
  actions: {
    save: function() {
      var self = this;
      var site = this.get('model');
      site.setProperties({
        newName: (this.get('newName') !== site.get('id')) ? this.get('newName') : '',
        isReady: false
      });
      var promise = site.save();
      promise.then(function(){
        self.transitionToRoute("websites");
      }, function(e){
        handleModelError(self, e);
      });
    },
    redirect: function() {
      this.get('model').rollback();
      this.transitionToRoute('websites');
    },
    openModal: function(name) {
      Ember.$('.ui.' + name + '.modal').modal('show');
    },
    deleteSite: function(){
      this.set('model.isReady', false);
      Ember.$.ajax(`${ENV.APP.krakenHost}/api/websites/${this.get('model.id')}`, {type: 'DELETE'});
      this.transitionToRoute('websites');
    },
    siteAction: function(action) {
      var self = this;
      Ember.$.ajax(`${ENV.APP.krakenHost}/api/websites/actions/${this.get("model.id")}/${action}`, {type: "POST"})
        .done(function() {
          self.notifications.new("success", action+" action completed successfully");
        })
        .fail(function(e) {
          handleModelError(self, e);
        });
    }
  }
});
