import Ember from "ember";
import ENV from "../config/environment";
import Pollster from "../objects/pollster";
import {showFade, showLoader, hideLoader, hideFade} from "../utils/loading";


export default Ember.Route.extend({
  init: function() {
    var self = this;
    var initConfig = $.getJSON(ENV.APP.krakenHost+'/config', function(j){
      ENV.APP.dateFormat = j.config.general.date_format;
      ENV.APP.timeFormat = j.config.general.time_format;
    });
    initConfig.fail(function(){
      self.message.error('Could not get initial configuration, reverting to defaults.');
    });
    this._super();
  },
  setupController: function() {
    if (Ember.isNone(this.get('pollster'))) {
      var self = this;
      this.set('pollster', Pollster.create({
        onPoll: function() {
          $.getJSON(ENV.APP.krakenHost+'/genesis').then(function(j) {
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
    error: function(model) {
      console.log(model);
      return true;
    },
    loading: function(transition, originRoute) {
      showFade();
      showLoader();
      var self = this;
      transition.then(function(){
        Ember.run.schedule('afterRender', self, function(){
          hideLoader();
          hideFade();
        });
      })
    },
    showModal: function(name, model, extra) {
      if (extra) model.set('extra', extra);
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
        url: ENV.APP.krakenHost+'/system/shutdown',
        type: 'POST'
      });
    },
    reboot: function() {
      $.ajax({
        url: ENV.APP.krakenHost+'/system/reboot',
        type: 'POST'
      });
    }
  }
});
