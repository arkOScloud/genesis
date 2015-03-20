import DS from "ember-data";


export default DS.Model.extend({
    version: DS.attr('string'),
    upgradable: DS.attr('string'),
    isUpgradable: function() {
      return this.get('upgradable')!="false";
    }.property('upgradable'),
    architecture: DS.attr('string'),
    buildDate: DS.attr('string'),
    conflictsWith: DS.attr('string'),
    dependsOn: DS.attr('string'),
    description: DS.attr('string'),
    groups: DS.attr('string'),
    installDate: DS.attr('string'),
    installReason: DS.attr('string'),
    installScript: DS.attr('string'),
    installedSize: DS.attr('string'),
    licenses: DS.attr('string'),
    optionalDeps: DS.attr('string'),
    optionalFor: DS.attr('string'),
    packager: DS.attr('string'),
    provides: DS.attr('string'),
    replaces: DS.attr('string'),
    requiredBy: DS.attr('string'),
    url: DS.attr('string'),
    validatedBy: DS.attr('string'),
    repo: DS.attr('string'),
    installed: DS.attr('boolean', {defaultValue: false}),
    operation: DS.attr('string', {defaultValue: ""}),
    toInstall: function() {
      return this.get('operation') == "install";
    }.property('operation'),
    toRemove: function() {
      return this.get('operation') == "remove";
    }.property('operation')
});
