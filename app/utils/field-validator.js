import Ember from "ember";


export default function fieldValidator(pre) {
  pre = pre || "";
  Ember.$(pre+' .form-group').removeClass('has-error has-success');
  Ember.$(pre+' input.required, '+pre+' textarea.required, '+pre+' select.required').each(function(){
    if (!Ember.$(this).val()) {
      Ember.$(this).parent('.form-group').addClass('has-error');
    }
  });
  Ember.$(pre+' input.username').each(function(){
    if (!/^[a-z_][a-z0-9_]{0,30}$/.test(Ember.$(this).val())) {
      Ember.$(this).parent('.form-group').addClass('has-error');
    }
  });
  if (Ember.$(pre+' input.password').length > 1) {
    var values = [];
    Ember.$(pre+' input.password').each(function(){
      if (Ember.$(this).val().length < 6 && (Ember.$(this).hasClass('required') || Ember.$(this).val().length > 0)) {
        Ember.$(this).parent('.form-group').addClass('has-error');
      }
      values[values.length] = Ember.$(this).val();
    });
    if (values[0] !== values[1]) {
      Ember.$(pre+' input.password').parent('.form-group').addClass('has-error');
    }
  }
  Ember.$(pre+' .form-group').not('.has-error').addClass('has-success');
}
