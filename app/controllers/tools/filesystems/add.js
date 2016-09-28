import Ember from 'ember';
import handleModelError from '../../../utils/handle-model-error';
import cardColor from '../../../utils/card-color';


export default Ember.Controller.extend({
  breadCrumb: {name: 'New virtual disk', icon: 'disk outline'},
  cardColor: function() {
    return cardColor();
  }.property(),
  fields: {
    name: {
      rules: [
        {
          type: 'empty'
        }
      ]
    },
    size: {
      rules: [
        {
          type: 'empty'
        },
        {
          type: 'integer'
        }
      ]
    },
    password: {
      rules: [
        {
          type: 'minLength[6]'
        },
        {
          type: 'empty'
        }
      ]
    },
    passwordConf: {
      rules: [
        {
          type: 'match[password]'
        }
      ]
    }
  },
  actions: {
    save: function(){
      var self = this;
      var fs = self.store.createRecord('filesystem', {
        id: this.get('id'),
        size: parseInt(this.get('size')) * 1024 * 1024,
        crypt: this.get('crypt') || false,
        passwd: this.get('passwd'),
        isReady: false
      });
      var promise = fs.save();
      promise.then(function(){
        self.setProperties({id: '', size: '', crypt: false, passwd: '', passwdb: ''});
        self.transitionToRoute("tools.filesystems");
      }, function(e){
        handleModelError(self, e);
        fs.deleteRecord();
      });
    },
    redirect: function() {
      this.setProperties({id: '', size: '', crypt: false, passwd: '', passwdb: ''});
      this.transitionToRoute('tools.filesystems');
    }
  }
});
