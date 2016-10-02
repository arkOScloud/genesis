import DS from "ember-data";
import ENV from "../config/environment";
import cardColor from "../utils/card-color";


export default DS.Model.extend({
    name: DS.attr('string'),
    icon: DS.attr('string'),
    type: DS.attr('string'),
    prettyType: function() {
      return this.get('type').capitalize();
    }.property('type'),
    version: DS.attr('string'),
    error: DS.attr('string'),
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
        return `${ENV.APP.krakenHost}/api/apps/assets/${this.get('id')}/logo.png`;
      } else if (!this.get('installed') && this.get('assets').logo) {
        return `${ENV.APP.GRMHost}/api/v1/assets/${this.get('assets').logo}`;
      } else {
        return null;
      }
    }.property('logo', 'installed', 'assets'),
    cardColor: function() {
      return cardColor();
    }.property(),
    modules: DS.attr(),
    screenshots: DS.attr(),
    screenshotUrls: function() {
      var shots = [];
      if (this.get('assets') && this.get('assets').screens) {
        this.get('assets').screens.forEach(function(i) {
          shots.push(`${ENV.APP.GRMHost}/api/v1/assets/${i}`);
        });
      }
      return shots;
    }.property('assets'),
    services: DS.attr(),
    databaseEngines: DS.attr(),
    databaseMultiuser: DS.attr('boolean', {defaultValue: false}),
    databaseService: DS.attr('string'),
    downloadUrl: DS.attr('string'),
    usesPhp: DS.attr('boolean', {defaultValue: false}),
    usesSsl: DS.attr('boolean', {defaultValue: false}),
    selectedDbengine: DS.attr('string'),
    websiteDefaultDataSubdir: DS.attr('string'),
    websiteActions: DS.attr(),
    websiteOptions: DS.attr(),
    websiteDatapaths: DS.attr('boolean', {defaultValue: false}),
    websiteUpdates: DS.attr('boolean', {defaultValue: false}),
    installed: DS.attr('boolean', {defaultValue: false}),
    upgradable: DS.attr('string'),
    isUpgradable: function() {
      return !!this.get('upgradable');
    }.property('upgradable'),
    displayInMenu: function() {
      var goodType  = ["app", "website", "fileshare"].indexOf(this.get('type'))>=0,
          installed = this.get('installed'),
          loadable  = this.get('loadable');
      return (goodType && loadable && installed);
    }.property('type', 'loadable', 'installed'),
    operation: DS.attr('string'),
    isReady: DS.attr('boolean', {defaultValue: false})
});
