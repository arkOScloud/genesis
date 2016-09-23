import Ember from "ember";
import ENV from "../config/environment";


export default Ember.Component.extend({
  classNameBindings: [':ui-fm-item', 'item.selected:ui-fm-selected:'],
  open: 'open',
  menu: 'menu',
  href: function(){
    return ENV.APP.krakenHost+"/api/files/"+this.get('item.id')+"?download=true";
  }.property('item'),
  initContextMenu: function() {
    var self = this;
    Ember.$('#'+this.get('elementId')).bind('contextmenu', function() {
      if (self.get('files.selectedItems.length') && self.get('files.selectedItems').indexOf(self.get("item")) === -1) {
        self.get('files.currentFolder').setEach('selected', false);
      }
      self.set('item.selected', true);
      Ember.$('#context-sidebar').sidebar('toggle');
      return false;
    });
  }.on('didInsertElement'),
  click: function() {
    if (window.CTRL) {
      this.set('item.selected', !this.get('item.selected'));
    } else {
      this.sendAction('open', this.get('item'));
    }
  }
});
