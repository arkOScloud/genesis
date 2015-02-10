Genesis.GWizardmodalComponent = Ember.Component.extend({
  firstStep: function() {
    return this.get('control').get('step')==1;
  }.property('control.step'),
  lastStep: function() {
    return this.get('control').get('step')==this.get('control').get('last');
  }.property('control.step'),
  actions: {
    ok: function() {
      var self = this,
          last = this.get('control').get('last');
      if (this.get('control').get('validateFields').indexOf(last)>=0) {
        Genesis.FieldValidator('#wizardstep'+last);
        setTimeout(function(){
          if ($('#wizardstep'+last+' .form-group.has-error').length == 0) {
            self.$('.modal').modal('hide');
            self.sendAction('ok');
          };
        }, 1000);
      } else {
        self.$('.modal').modal('hide');
        self.sendAction('ok');
      }
    },
    previous: function() {
      var step = this.get('control').get('step');
      $('#wizardstep'+step).hide();
      this.get('control').set('step', step-1);
      $('#wizardstep'+(step-1)).show();
    },
    next: function() {
      var self = this,
          step = this.get('control').get('step');
      if (this.get('control').get('validateFields').indexOf(step)>0) {
        Genesis.FieldValidator('#wizardstep'+step);
        setTimeout(function(){
          if ($('#wizardstep'+step+' .form-group.has-error').length == 0) {
            $('#wizardstep'+step).hide();
            self.get('control').set('step', step+1);
            $('#wizardstep'+(step+1)).show();
          };
        }, 1000);
      } else {
        $('#wizardstep'+step).hide();
        this.get('control').set('step', step+1);
        $('#wizardstep'+(step+1)).show();
      };
    }
  },
  show: function() {
    this.$('.modal').modal().on('hidden.bs.modal', function() {
      this.sendAction('close');
    }.bind(this));
  }.on('didInsertElement')
});

Genesis.GWizardstepComponent = Ember.Component.extend({
  stepId: function() {
    return 'wizardstep'+this.step;
  }.property(),
  hidden: function() {
    return this.step!=1?'display:none;':'';
  }.property()
});
