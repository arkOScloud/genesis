import Ember from "ember";
/* global jQuery */


jQuery.fn.center = function () {
    this.css("position","absolute");
    this.css("top", Math.max(0, ((Ember.$(window).height() - Ember.$(this).outerHeight()) / 2) +
                                                Ember.$(window).scrollTop()) + "px");
    this.css("left", Math.max(0, ((Ember.$(window).width() - Ember.$(this).outerWidth()) / 2) +
                                                Ember.$(window).scrollLeft()) + "px");
    return this;
};

export function showFade(f) {
  Ember.$('.ui-fade').stop().center().fadeIn(200, function(){
    if (f) {
      f();
    }
  });
}

export function showLoader(f) {
  Ember.$('.ui-loader').stop().center().fadeIn(200, function(){
    if (f) {
      f();
    }
  });
}

export function hideFade() {
  Ember.$('.ui-fade').stop().fadeOut(200);
}

export function hideLoader() {
  Ember.$('.ui-loader').stop().fadeOut(200);
}
