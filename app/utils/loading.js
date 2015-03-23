export function showFade(f) {
  $('.ui-fade').stop().fadeIn(200, function(){
    if (f) f();
  });
};

export function showLoader(f) {
  $('.ui-loader').stop().fadeIn(200, function(){
    if (f) f();
  });
};

export function hideFade() {
  $('.ui-fade').stop().fadeOut(200);
};

export function hideLoader() {
  $('.ui-loader').stop().fadeOut(200);
};
