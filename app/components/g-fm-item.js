import Ember from "ember";
import ENV from "../config/environment";


export default Ember.Component.extend({
  classNameBindings: [':ui-fm-item', 'item.selected:text-primary:'],
  open: 'open',
  menu: 'menu',
  href: function(){
    return ENV.APP.krakenHost+"/files/"+this.get('item.id')+"?download=true";
  }.property('item'),
  initContextMenu: function() {
    var self = this;
    $('#'+this.get('elementId')).contextmenu({
      target: '#context-menu', 
      before: function(e, context) {
        if (self.get('files.selectedItems.length') && self.get('files.selectedItems').indexOf(self.get("item"))==-1) {
          self.get('files.currentFolder').setEach('selected', false);
        };
        self.set('item.selected', true);
        return true;
      }
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
