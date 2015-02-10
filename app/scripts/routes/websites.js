Genesis.WebsitesRoute = Ember.Route.extend({
  model: function() {
    return Ember.RSVP.hash({
      sites: this.get('store').find('website'),
      apps: this.get('store').find('app', {type: "website"})
    });
  },
  actions: {
    delete: function(model){
      model.set('isReady', false);
      $.ajax({
        url: Genesis.Config.krakenHost+'/websites/'+model.get('id'),
        type: 'DELETE'
      });
    }
  }
});
