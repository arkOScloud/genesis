var Genesis = window.Genesis = Ember.Application.create();

Genesis.initializer({
  name: "registerMessages",
  initialize: function(container, application) {
    application.register('message:main', Genesis.Messager);
  }
});

Genesis.initializer({
  name: "injectMessages",
  initialize: function(container, application) {
    application.inject('controller', 'message', 'message:main');
    application.inject('component',  'message', 'message:main');
    application.inject('adapter',    'message', 'message:main');
    application.inject('route',      'message', 'message:main');
  }
});

Genesis.Config = {
    krakenHost: 'http://localhost:8765',
    currentVersion: '0.7.0'
};

Genesis.FieldValidator = function(pre) {
    pre = pre || "";
    $(pre+' .form-group').removeClass('has-error has-success');
    $(pre+' input.required').each(function(i){
        if (!$(this).val()) {
            $(this).parent('.form-group').addClass('has-error');
        };
    });
    $(pre+' input.username').each(function(i){
      if (!/^[a-z_][a-z0-9_]{0,30}$/.test($(this).val())) {
          $(this).parent('.form-group').addClass('has-error');
      };
    });
    if ($(pre+' input.password').length > 1) {
        var values = [];
        $(pre+' input.password').each(function(i){
            if ($(this).val().length < 6 && ($(this).hasClass('required') || $(this).val().length > 0)) {
                $(this).parent('.form-group').addClass('has-error');
            };
            values[values.length] = $(this).val();
        });
        if (values[0] != values[1]) {
            $(pre+' input.password').parent('.form-group').addClass('has-error');
        };
    };
    $(pre+' .form-group').not('.has-error').addClass('has-success');
};

Genesis.Message = Ember.Object.extend();

Genesis.Messager = Ember.ArrayProxy.extend({
  content: Ember.A(),
  timeout: 3000,
  pushObject: function(object) {
    object.typeClass = 'alert-' + object.type;
    Ember.run.later(function() {
      if (object.dismissable && ["info", "success"].indexOf(object.type)>=0) {
        $('#'+object.id).alert('close');
      };
    }, this.get('timeout'));
    var exists = this.content.filterBy('id', object.id);
    if (exists.length) {
      exists[0].set('type', object.type);
      exists[0].set('typeClass', object.typeClass);
      exists[0].set('icon', object.icon);
      exists[0].set('message', object.message);
      exists[0].set('dismissable', object.dismissable);
    } else {
      object = Genesis.Message.create(object);
      this._super(object);
    };
  },
  danger: function(message, id, dismissable) {
    id = id || Math.random().toString(36).substring(10);
    this.pushObject({
      id: id,
      type: 'danger',
      icon: 'fa fa-exclamation-circle',
      message: message,
      dismissable: typeof dismissable !== 'undefined' ? dismissable : true
    });
  },
  warning: function(message, id, dismissable) {
    id = id || Math.random().toString(36).substring(10);
    this.pushObject({
      id: id,
      type: 'warning',
      icon: 'fa fa-exclamation-triangle',
      message: message,
      dismissable: typeof dismissable !== 'undefined' ? dismissable : true
    });
  },
  info: function(message, id, dismissable) {
    id = id || Math.random().toString(36).substring(10);
    this.pushObject({
      id: id,
      type: 'info',
      icon: 'fa fa-info-circle',
      message: message,
      dismissable: typeof dismissable !== 'undefined' ? dismissable : true
    });
  },
  success: function(message, id, dismissable) {
    id = id || Math.random().toString(36).substring(10);
    this.pushObject({
      id: id,
      type: 'success',
      icon: 'fa fa-thumbs-up',
      message: message,
      dismissable: typeof dismissable !== 'undefined' ? dismissable : true
    });
  }
});

Genesis.Pollster = Ember.Object.extend({
  interval: function() {
    return 2000; // Time between polls (in ms)
  }.property().readOnly(),
  schedule: function(f) {
    return Ember.run.later(this, function() {
      f.apply(this);
      this.set('timer', this.schedule(f));
    }, this.get('interval'));
  },
  stop: function() {
    Ember.run.cancel(this.get('timer'));
  },
  start: function() {
    this.set('timer', this.schedule(this.get('onPoll')));
  },
  onPoll: function(){
    // Do some work
  }
});

/* Order and include as you please. */
require('scripts/controllers/*');
require('scripts/store');
require('scripts/models/*');
require('scripts/routes/*');
require('scripts/components/*');
require('scripts/views/*');
require('scripts/adapters/*');
require('scripts/serializers/*');
require('scripts/router');
require('scripts/extra/*');
