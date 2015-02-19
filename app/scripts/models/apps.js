Genesis.App = DS.Model.extend({
    name: DS.attr('string'),
    icon: DS.attr('string'),
    type: DS.attr('string'),
    version: DS.attr('string'),
    error: DS.attr('boolean', {defaultValue: false}),
    appAuthor: DS.attr('string'),
    appHomepage: DS.attr('string'),
    author: DS.attr('string'),
    categories: DS.attr('string'),
    dependencies: DS.attr(),
    description: DS.attr(),
    generation: DS.attr('number'),
    homepage: DS.attr('string'),
    loadable: DS.attr('boolean', {defaultValue: false}),
    logo: DS.attr('boolean', {defaultValue: false}),
    logoURL: function() {
      return this.get('logo')?Genesis.Config.krakenHost+'/apps/logo/'+this.get('id'):null;
    }.property('logo'),
    modules: DS.attr(),
    screenshots: DS.attr(),
    services: DS.attr(),
    database_engines: DS.attr(),
    databaseMultiuser: DS.attr('boolean', {defaultValue: false}),
    download_url: DS.attr('string'),
    uses_php: DS.attr('boolean', {defaultValue: false}),
    uses_ssl: DS.attr('boolean', {defaultValue: false}),
    website_datapaths: DS.attr('boolean', {defaultValue: false}),
    website_default_data_subdir: DS.attr('string'),
    website_updates: DS.attr('boolean', {defaultValue: false}),
    displayInMenu: function() {
      var goodType = ["app", "website"].indexOf(this.get('type'))>=0,
          loadable = this.get('loadable');
      return (goodType && loadable);
    }.property('type', 'loadable'),
    displayHref: function() {
      if (this.get('type') == "website") {
        return 'websites';
      } else {
        return 'apps/'+this.get('id');
      };
    }.property('id', 'type')
});
