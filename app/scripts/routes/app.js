Genesis.ApplicationRoute = Ember.Route.extend({
  setupController: function() {
    if (Ember.isNone(this.get('pollster'))) {
      this.set('pollster', Genesis.Pollster.create({
        onPoll: function() {
          $.getJSON(Genesis.Config.krakenHost+'/messages').then(function(j) {
            j.messages.forEach(function(m) {
              var ico = "fa fa-info-circle";
              var clss = "info"
              if (m.class == "success") {
                ico = "fa fa-thumbs-up";
                clss = "success";
              } else if (m.class == "warn") {
                ico = "fa fa-exclamation-triangle";
                clss = "warning";
              } else if (m.class == "error") {
                ico = "fa fa-exclamation-circle";
                clss = "danger";
              };
              if ($('#'+m.id).length>=1) {
                $('#'+m.id).removeClass('alert-success alert-info alert-warning alert-danger');
                $('#'+m.id).addClass(clss);
                if (m.complete) {
                  $('#'+m.id).addClass('alert-dismissable');
                  $('#'+m.id).html('<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&#215;</button><i class="'+ico+'" style="line-height:1;"></i> '+m.message);
                  if (clss != "warning" && clss != "danger") {
                    setTimeout(function () {$('#'+m.id).alert('close')}, 3000);
                  };
                } else {
                  $('#'+m.id).html('<i class="'+ico+'" style="line-height:1;"></i> '+m.message);
                };
              } else if (m.complete) {
                $('#message-box').append('<div id="'+m.id+'" class="alert alert-'+clss+' alert-dismissable fade in"><button type="button" class="close" data-dismiss="alert" aria-hidden="true">&#215;</button><i class="'+ico+'" style="line-height:1;"></i> '+m.message+'</div>');
                if (clss != "warning" && clss != "danger") {
                  setTimeout(function () {$('#'+m.id).alert('close')}, 3000);
                };
              } else {
                $('#message-box').append('<div id="'+m.id+'" class="alert alert-'+clss+' fade in"><i class="'+ico+'" style="line-height:1;"></i> '+m.message+'</div>');
              };
            })
          });
        }
      }));
    }
    this.get('pollster').start();
  },
  deactivate: function() {
    this.get('pollster').stop();
  },
  actions: {
    showModal: function(name, model, extra) {
      model.extra = extra;
      this.render(name, {
        into: 'application',
        outlet: 'modal',
        model: model
      });
    },
    showConfirm: function(action, text, model) {
      model.set('confirmAction', action);
      model.set('confirmText', text);
      this.render('components/g-confirm', {
        into: 'application',
        outlet: 'modal',
        model: model
      });
    },
    removeModal: function() {
      this.disconnectOutlet({
        outlet: 'modal',
        parentView: 'application'
      });
    }
  }
});

Genesis.IndexRoute = Ember.Route.extend({
  model: function() {
    return this.get('store').find('app');
  }
});
