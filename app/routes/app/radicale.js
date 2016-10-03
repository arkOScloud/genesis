import Ember from "ember";
import ENV from "../../config/environment";


export default Ember.Route.extend({
  renderTemplate: function() {
    this.render('app.radicale', { into: 'application' });
  },
  model: function() {
    return Ember.RSVP.hash({
      calendars: this.get('store').find('calendar'),
      addressBooks: this.get('store').find('addressBook'),
      domains: this.get('store').find('domain'),
      status: Ember.$.getJSON(ENV.APP.krakenHost+'/api/apps/radicale/setup')
    });
  }
});
