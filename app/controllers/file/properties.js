import Ember from "ember";
import ENV from "../../config/environment";


export default Ember.ObjectController.extend({
  perms: {},
  setPermObject: function(){
    var p = this.get("model.perms.str");
    this.set("perms", {
      user: {
        read: p[0]=="r",
        write: p[1]=="w",
        execute: p[2]=="x"
      },
      group: {
        read: p[3]=="r",
        write: p[4]=="w",
        execute: p[5]=="x"
      },
      all: {
        read: p[6]=="r",
        write: p[7]=="w",
        execute: p[8]=="x"
      }
    });
  }.observes('model.perms.str'),
  actions: {
    save: function() {
      var self = this,
          poct = "0",
          file = this.get("model"),
          p = this.get("perms");
      poct += String((p.user.read?4:0)+(p.user.write?2:0)+(p.user.execute?1:0));
      poct += String((p.group.read?4:0)+(p.group.write?2:0)+(p.group.execute?1:0));
      poct += String((p.all.read?4:0)+(p.all.write?2:0)+(p.all.execute?1:0));
      file = JSON.parse(JSON.stringify(file));
      file.perms.oct = poct;
      file.operation = "props";
      $.ajax({
        url: ENV.APP.krakenHost+'/files/'+file.id,
        type: "PUT",
        data: JSON.stringify({file: file}),
        contentType: 'application/json',
        processData: false,
        success: function(j) {
          self.message.success("Permissions changed successfully");
        },
        error: function(j) {
          if (e.status == 500) self.transitionToRoute("error", e);
          self.message.danger(j.responseJSON.message);
        }
      });
    }
  }
});
