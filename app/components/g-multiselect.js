import Ember from "ember";


export default Ember.Component.extend({
  _initializeMulti: (function() {
    return $(".multi").multiSelect({
      afterInit: (function(_this) {
        return function(controller) {
          if (_this.selected) {
            $('.multi').multiSelect('select', _this.selected);
          }
        }
      })(this),

      afterSelect: (function(_this) {
        return function(values) {
          return _this.sendAction("addAction", values);
        };
      })(this),

      afterDeselect: (function(_this) {
        return function(values) {
          return _this.sendAction("removeAction", values);
        };
      })(this)

    });
  }).on("didInsertElement")
});
