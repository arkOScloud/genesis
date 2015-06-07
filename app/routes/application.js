import Ember from "ember";
import Router from "../router";
import ENV from "../config/environment";
import Pollster from "../objects/pollster";
import {showFade, showLoader, hideLoader, hideFade} from "../utils/loading";
import ApplicationRouteMixin from 'simple-auth/mixins/application-route-mixin';


export default Ember.Route.extend(ApplicationRouteMixin, {
  setupController: function() {
    if (this.get("session.isAuthenticated")) {
      this.setupParallelCalls();
    };
  },
  setupParallelCalls: function() {
    var self = this;
    $.getJSON(ENV.APP.krakenHost+'/api/apps', function(m){
      m.apps.forEach(function(i){
        if (i.type=='app' && i.installed) {
          Router.map(function(){
            this.route(i.id);
          });
        };
      });
    });
    if (Ember.isNone(this.get('pollster'))) {
      this.set('pollster', Pollster.create({
        onPoll: function() {
          $.getJSON(ENV.APP.krakenHost+'/api/genesis').then(function(j) {
            if (j && j.messages) {
              j.messages.forEach(function(m) {
                if (m.class == "success" && !ENV.APP.needsFirstRun) {
                  self.message.success(m.message, m.id, m.complete, m.headline);
                } else if (m.class == "warn") {
                  self.message.warning(m.message, m.id, m.complete, m.headline);
                } else if (m.class == "error") {
                  self.message.danger(m.message, m.id, m.complete, m.headline);
                } else if (!ENV.APP.needsFirstRun) {
                  self.message.info(m.message, m.id, m.complete, m.headline);
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
      this.get('pollster').start();
    };
  },
  deactivate: function() {
    this.get('pollster').stop();
  },
  actions: {
    sessionAuthenticationSucceeded: function() {
      this.setupParallelCalls();
      this._super();
    },
    sessionAuthenticationFailed: function(err) {
      var msg = "";
      if (err.message == "Invalid credentials") {
        msg = "Username or password incorrect.";
      } else if (err.message == "Not an admin user") {
        msg = "This user does not have administration rights.";
      } else {
        msg = "Unknown error, please check server."
      };
      this.controllerFor("login").set("loginMessage", msg);
    },
    authorizationFailed: function() {
      if (this.get('pollster')) {
        this.get('pollster').stop();
      };
      this._super();
    },
    willTransition: function(transition) {
      if (transition.targetName != "firstrun" && ENV.APP.needsFirstRun) {
        transition.abort();
        this.transitionTo('firstrun');
      };
    },
    error: function(error, transition) {
      var self = this;
      hideLoader();
      hideFade();
      return true;
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
        url: ENV.APP.krakenHost+'/api/system/shutdown',
        type: 'POST'
      });
    },
    reload: function() {
      $.ajax({
        url: ENV.APP.krakenHost+'/api/system/reload',
        type: 'POST'
      });
    },
    reboot: function() {
      $.ajax({
        url: ENV.APP.krakenHost+'/api/system/reboot',
        type: 'POST'
      });
    }
  }
});
