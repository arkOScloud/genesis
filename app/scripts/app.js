var Genesis = window.Genesis = Ember.Application.create();

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

Genesis.addMessage = function(cls, msg, id) {
  var ico = "fa fa-info-circle";
  var clss = "info"
  if (cls == "success") {
    ico = "fa fa-thumbs-up";
    clss = "success";
  } else if (cls == "warn") {
    ico = "fa fa-exclamation-triangle";
    clss = "warning";
  } else if (cls == "error") {
    ico = "fa fa-exclamation-circle";
    clss = "danger";
  };
  id = id || Math.random().toString(36).substring(7);
  $('#message-box').append('<div id="'+id+'" class="alert alert-'+clss+' alert-dismissable fade in"><button type="button" class="close" data-dismiss="alert" aria-hidden="true">&#215;</button><i class="'+ico+'" style="line-height:1;"></i> '+msg+'</div>');
  if (cls != "warn" && cls != "error") {
    setTimeout(function () {$('#'+id).alert('close')}, 3000);
  };
};

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
