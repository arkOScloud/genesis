import Ember from 'ember';


export default Ember.Controller.extend({
  breadCrumb: {name: 'New website', icon: 'fa-globe'},
  queryParams: ['siteType'],
  siteType: null,
  confirmedSiteType: null,
  websiteOptions: {},
  selectedSiteType: function() {
    return this.get('siteTypes').filterBy('id', this.get('siteType')).get('firstObject');
  }.property('siteType'),
  bumpWebsiteOptions: function() {
    return this.set('websiteOptions', this.get('confirmedSiteType.websiteOptions'));
  }.observes('confirmedSiteType'),
  canChooseDBType: function() {
    var dbe = this.get('confirmedSiteType.databaseEngines');
    return (dbe && dbe.get('length')>1);
  }.property('confirmedSiteType'),

  actions: {
    selectSiteType: function(siteType) {
      this.set('siteType', siteType.get('id'));
    },
    confirmSiteType: function() {
      this.set('confirmedSiteType', this.get('selectedSiteType'));
    },
    resetSiteType: function() {
      this.set('siteType', null);
      this.set('confirmedSiteType', null);
    },
    createWebsite: function() {
      var self = this;
      var extraData = {
        datadir: this.get("newSiteDataDir") || null,
        dbengine: this.get("canChooseDBType") ? (this.get("newSiteDBEngine") || this.get("availableDBTypes.firstObject")) : null
      };
      Ember.$('#new-website-form').form({
        fields: {
          name: ['regExp[/^[a-zA-Z0-9_]+$/]', 'empty'],
          port: ['integer[1..65536]', 'empty']
        },
        inline: true,
        keyboardShortcuts: false,
        onSuccess: function() {
          ["text", "password", "users", "boolean"].forEach(function(t) {
            if (!!self.get('websiteOptions.' + t)) {
              self.get('websiteOptions.' + t).forEach(function(i) {
                extraData[i.id] = extraData[i.value];
              });
            }
          });
          var site = self.store.createRecord('website', {
            id: self.get('newSiteName'),
            siteType: self.get('confirmedSiteType'),
            siteName: self.get('confirmedSiteType.name'),
            siteIcon: self.get('confirmedSiteType.icon'),
            domain: self.get('newSiteDomain') || self.get('domains.firstObject'),
            port: self.get('newSitePort'),
            extraData: extraData
          });
          var promise = site.save();
          promise.then(function(){
            self.transitionToRoute("websites");
          }, function(e){
            if (e.status === 500) {
              self.transitionToRoute("error", e);
            }
          });
        }
      });
      Ember.$('#new-website-form').form('validate form');
    }
  }
});
