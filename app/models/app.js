import DS from "ember-data";
import ENV from "../config/environment";


export default DS.Model.extend({
    name: DS.attr('string'),
    icon: DS.attr('string'),
    type: DS.attr('string'),
    prettyType: function() {
      return this.get('type').capitalize();
    }.property('type'),
    version: DS.attr('string'),
    error: DS.attr('boolean', {defaultValue: false}),
    appAuthor: DS.attr('string'),
    appHomepage: DS.attr('string'),
    author: DS.attr('string'),
    categories: DS.attr(),
    categoryString: function() {
      var cats = [];
      this.get('categories').forEach(function(i) {
        cats.push(i.primary+(i.secondary.length?": ":"")+i.secondary.join(", "));
      });
      return cats.join("; ");
    }.property('categories'),
    dependencies: DS.attr(),
    description: DS.attr(),
    generation: DS.attr('number'),
    homepage: DS.attr('string'),
    loadable: DS.attr('boolean', {defaultValue: false}),
    logo: DS.attr('boolean', {defaultValue: false}),
    assets: DS.attr(),
    logoURL: function() {
      if (this.get('installed') && this.get('logo')) {
        return ENV.APP.krakenHost+'/apps/logo/'+this.get('id');
      } else if (!this.get('installed') && this.get('assets').logo) {
        return ENV.APP.GRMHost+'/api/v1/assets/'+this.get('assets').logo;
      } else {
        return null;
      }
    }.property('logo', 'installed', 'assets'),
    modules: DS.attr(),
    screenshots: DS.attr(),
    screenshotUrls: function() {
      var shots = [];
      if (this.get('assets') && this.get('assets').screens) {
        this.get('assets').screens.forEach(function(i) {
          shots.push(ENV.APP.GRMHost+'/api/v1/assets/'+i);
        });
      }
      return shots;
    }.property('assets'),
    services: DS.attr(),
    database_engines: DS.attr(),
    databaseMultiuser: DS.attr('boolean', {defaultValue: false}),
    download_url: DS.attr('string'),
    uses_php: DS.attr('boolean', {defaultValue: false}),
    uses_ssl: DS.attr('boolean', {defaultValue: false}),
    website_datapaths: DS.attr('boolean', {defaultValue: false}),
    website_default_data_subdir: DS.attr('string'),
    website_updates: DS.attr('boolean', {defaultValue: false}),
    installed: DS.attr('boolean', {defaultValue: false}),
    upgradable: DS.attr('string'),
    isUpgradable: function() {
      return !!this.get('upgradable');
    }.property('upgradable'),
    displayInMenu: function() {
      var goodType  = ["app", "website"].indexOf(this.get('type'))>=0,
          installed = this.get('installed'),
          loadable  = this.get('loadable');
      return (goodType && loadable && installed);
    }.property('type', 'loadable', 'installed'),
    displayHref: function() {
      if (this.get('type') == "website") {
        return 'websites';
      } else {
        return 'apps/'+this.get('id');
      };
    }.property('id', 'type'),
    operation: DS.attr('string'),
    isReady: DS.attr('boolean', {defaultValue: false})
});
