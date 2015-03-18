Genesis.GFmItemComponent = Ember.Component.extend({
  classNameBindings: [':ui-fm-item', 'item.selected:text-primary:'],
  open: 'open',
  menu: 'menu',
  click: function() {
    if (Genesis.CTRL) {
      this.set('item.selected', !this.get('item.selected'));
    } else {
      this.sendAction('open', this.get('item'));
    }
  },
  contextMenu: function() {
    this.sendAction('menu', this.get('item'));
    return false;
  }
});
