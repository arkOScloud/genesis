jQuery.fn.center = function () {
    this.css("position","absolute");
    this.css("top", Math.max(0, (($(window).height() - $(this).outerHeight()) / 2) +
                                                $(window).scrollTop()) + "px");
    this.css("left", Math.max(0, (($(window).width() - $(this).outerWidth()) / 2) +
                                                $(window).scrollLeft()) + "px");
    return this;
};

export function showFade(f) {
  $('.ui-fade').stop().center().fadeIn(200, function(){
    if (f) f();
  });
};

export function showLoader(f) {
  $('.ui-loader').stop().center().fadeIn(200, function(){
    if (f) f();
  });
};

export function hideFade() {
  $('.ui-fade').stop().fadeOut(200);
};

export function hideLoader() {
  $('.ui-loader').stop().fadeOut(200);
};
