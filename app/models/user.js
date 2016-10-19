import DS from "ember-data";
import cardColor from "../utils/card-color";


export default DS.Model.extend({
    name: DS.attr('string'),
    firstName: DS.attr('string'),
    lastName: DS.attr('string'),
    fullName: DS.attr('string'),
    admin: DS.attr('boolean', {defaultValue: false}),
    sudo: DS.attr('boolean', {defaultValue: false}),
    domain: DS.belongsTo('domain', {async: true}),
    passwd: DS.attr('string'),
    isReady: DS.attr('boolean', {defaultValue: false}),
    mailAddresses: DS.attr(),
    selectId: function() {
      return this.get('name');
    }.property('name'),
    selectText: function() {
      return this.get('name');
    }.property('name'),
    cardColor: function() {
      return cardColor();
    }.property()
});
