import Ember from "ember";
/* global CodeMirror */


export default Ember.Component.extend({
  initCodeMirror: function() {
    var cm,
        self = this,
        file = this.get('file');
    Ember.$('.modal').on('shown.bs.modal', function(){
      cm = CodeMirror.fromTextArea(document.getElementById("codemirror"), {
        lineNumbers: true,
        mode: file.mimetype?file.mimetype:"shell"
      });
      self.set("output", cm.getValue());
      cm.on("change", function(){
        self.set("output", cm.getValue());
      });
    });
  }.on('didInsertElement')
});
