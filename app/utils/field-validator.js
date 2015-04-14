export default function fieldValidator(pre) {
    pre = pre || "";
    $(pre+' .form-group').removeClass('has-error has-success');
    $(pre+' input.required, '+pre+' textarea.required, '+pre+' select.required').each(function(i){
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
