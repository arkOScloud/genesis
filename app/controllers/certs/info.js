import Ember from 'ember';

export default Ember.Controller.extend({
  breadCrumb: Ember.computed("model.id", {
    get() {
      return {name: this.get("model.id"), icon: 'fa-certificate'};
    }
  }),
  actions: {
    save: function(){
      var self    = this,
          cert    = this.get('model'),
          avail   = this.get('model.extra.assns.certassigns'),
          assigns = [];
      this.get('assignsSelected').forEach(function(i){
        assigns.pushObject(avail.filterBy('id', i)[0]);
      });
      cert.set('assigns', assigns);
      cert.set('isReady', false);
      var promise = cert.save();
      promise.then(function(){}, function(e){
        if (e.status === 500) {
          self.transitionToRoute("error", e);
        }
      });
    },
    openModal: function(name) {
      Ember.$('.ui.' + name + '.modal').modal('show');
    },
    deleteCert: function() {
      var self = this;
      this.get('model').destroyRecord();
      Ember.$('.ui.delete-cert.modal').modal('hide', function() {
        self.transitionToRoute('certs');
      });
    }
  }
});
