import Ember from "ember";
import ENV from "../../config/environment";


export default Ember.ObjectController.extend({
  needs: ["files"],
  kh: ENV.APP.krakenHost,
  files: Ember.computed.alias('controllers.files.selectedItems')
});
