Genesis.ApplicationRoute = Ember.Route.extend({
  setupController: function() {
    if (Ember.isNone(this.get('pollster'))) {
      var self = this;
      this.set('pollster', Genesis.Pollster.create({
        onPoll: function() {
          $.getJSON(Genesis.Config.krakenHost+'/genesis').then(function(j) {
            if (j && j.messages) {
              j.messages.forEach(function(m) {
                if (m.class == "success") {
                  self.message.success(m.message, m.id, m.complete);
                } else if (m.class == "warn") {
                  self.message.warning(m.message, m.id, m.complete);
                } else if (m.class == "error") {
                  self.message.danger(m.message, m.id, m.complete);
                } else {
                  self.message.info(m.message, m.id, m.complete);
                };
              });
            };
            if (j && j.purges && !$.isEmptyObject(j.purges)) {
              j.purges.forEach(function(e) {
                var record = self.store.getById(e.model, e.id);
                if (record) self.store.unloadRecord(record);
              });
            };
            if (j && j.pushes && !$.isEmptyObject(j.pushes)) {
              self.store.pushPayload(j.pushes);
            };
          });
        }
      }));
    }
    this.get('pollster').start();
  },
  deactivate: function() {
    this.get('pollster').stop();
  },
  actions: {
    showModal: function(name, model, extra) {
      model.extra = extra;
      this.render(name, {
        into: 'application',
        outlet: 'modal',
        model: model
      });
    },
    showConfirm: function(action, text, model) {
      if (model) {
        model.set('confirmAction', action);
        model.set('confirmText', text);
      } else {
        model = {confirmAction: action, confirmText: text};
      };
      this.render('components/g-confirm', {
        into: 'application',
        outlet: 'modal',
        model: model
      });
    },
    removeModal: function() {
      this.disconnectOutlet({
        outlet: 'modal',
        parentView: 'application'
      });
    },
    shutdown: function() {
      $.ajax({
        url: Genesis.Config.krakenHost+'/system/shutdown',
        type: 'POST'
      });
    },
    reboot: function() {
      $.ajax({
        url: Genesis.Config.krakenHost+'/system/reboot',
        type: 'POST'
      });
    }
  }
});

Genesis.IndexRoute = Ember.Route.extend({
  model: function() {
    return this.get('store').find('app');
  }
});
