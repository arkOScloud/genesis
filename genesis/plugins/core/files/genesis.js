var Genesis;

var warning_button_id;

Genesis = (function() {
    var firstPasswordEntry = true;

    return {
	query: function (_uri, _data, _noupdate) {
	    $.ajax({
		url: _uri,
		data: _data,
		success: _noupdate?undefined:Genesis.Core.processResponse,
		error: Genesis.Core.processOffline,
		type: _data?'POST':'GET',
	    });
	    if (!_noupdate)
		Genesis.UI.showLoader(true);
	    return false;
	},

        verifyPassword: function(password1, password2, message, event){
	    
            if(event.target.id == password1 && firstPasswordEntry){
                return true;
            }
            firstPasswordEntry = false;
            var pass1 = document.getElementById(password1),
                pass2 = document.getElementById(password2),
                error = document.getElementById(message);
            var keycode = (event != undefined && typeof event.charCode !== "undefined") ? String.fromCharCode(event.charCode) : '';
            
            var match;
            if(event.target.id == password1){
                match = pass1.value + keycode == pass2.value;
            } else {
                match = pass1.value == pass2.value + keycode;
            }
                
            error.style.display = (match) ? 'none' : 'block';
            return match;
        },

	submit: function (fid, action) {
	    form = $('#'+fid);
	    if (form) {
		params = 'action=' + encodeURIComponent(action);
		url = $('input[type=hidden]', form)[0].value;

		$('input[type=text], input[type=password], input[type=hidden]', form).each(function (i,e) {
		    if (e.name != '__url')
			params += '&' + e.name + '=' + encodeURIComponent(e.value);
		});

		$('input[type=checkbox]', form).each(function (i,e) {
		    params += '&' + e.name + '=' + (e.checked?1:0);
		});

		$('input[type=radio]', form).each(function (i,e) {
		    if (e.checked)
			params += '&' + e.name + '=' + encodeURIComponent(e.value);
		});

		$('select:not([id$="-hints"])', form).each(function (i,e) {
		    params += "&" + e.name + "=" + encodeURIComponent(e.options[e.selectedIndex].value);
		});

		$('textarea', form).each(function (i,e) {
		    params += '&' + e.name + '=' + encodeURIComponent(e.value);
		});

		$('.ui-el-sortlist', form).each(function (i,e) {
		    var r = '';
		    $('>*', $(e)).each(function(i,e) {
			r += '|' + e.id;
		    });
		    params += '&' + e.id + '=' + encodeURIComponent(r);
		});

		Genesis.query(url, params);
	    }
	    return false;
	},

	init: function () {
	    Genesis.query('/handle/nothing');
	    Genesis.Core.requestProgress();
	},

	Core: {
	    processResponse: function (data) {
		$('.modal:not(#warningbox)').each( function (i, e) {
		    Genesis.UI.hideModal(e.id, true);
		});

		Genesis.UI.hideModal('warningbox');

		$('.twipsy').remove();

		$('#rightplaceholder').empty();
		$('#rightplaceholder').html(data);
		$('#rightplaceholder script').each(function (i,e) {
		    try {
			eval($(e).text);
		    } catch (err) { }
		    $(e).text('');
		});
		Genesis.UI.showLoader(false);
	    },

	    processOffline: function (data) {
		window.location.href = '/';
		Genesis.UI.showLoader(false);
	    },

	    requestProgress: function () {
		$.ajax({
		    url: '/core/progress',
		    success: function (j) {
			j = JSON.parse(j);
			$('#progress-box').empty();
			for (prg in j) {
			    if (j[prg].type === 'statusbox') {
				Genesis.Core.setStatusProgress(j[prg])
			    } else {
				Genesis.Core.addProgress(j[prg]);
			    };
			};
		    },
		    complete: function () {
			setTimeout('Genesis.Core.requestProgress()', 2000);
		    }
		});
	    },

	    addProgress: function (desc) {
		if (desc.can_abort) {
		    var html = '<div class="progress-box"><a class="close" onclick="return Genesis.showWarning(\'';
		    html += 'Cancel background task for ' + desc.owner + '?\', \'aborttask/' + desc.id + '\');">×</a>';
		} else {
		    var html = '<div class="progress-box">'
		};
		html += '<p><strong>' + desc.owner + '</strong> ' + desc.status + '</p></div>';
		$('#progress-box').append(html);
	    },

	    setStatusProgress: function (desc) {
		if (desc.status && $('#pbox-'+desc.id).length) {
		    $('#pbox-'+desc.id).text(desc.status);
		} else if (desc.status) {
		    $('html').scrollTop(0);
		    $('#whiteout').stop(true);
		    Genesis.UI.wipeOut(true);
		    status = '<p class="pbox-status" id="pbox-'+desc.id+'">'+desc.status+'</p>'
		    $('#pbox-text').append(status);
		    $('#pbox').show();
		    $('#pbox').center();
		} else if ($('#pbox').is(':visible')) {
		    $('#whiteout').stop(true);
		    Genesis.UI.wipeOut();
		    $('#pbox-text').empty();
		    $('#pbox').hide();
		    $('#whiteout').promise().done(function() {
			Genesis.query('/handle/nothing');
		    });
		} else if (!desc.status) {
			Genesis.query('/handle/nothing');
		};
	    },

	    clearStatusProgress: function () {
		$('#whiteout').stop(true);
		Genesis.UI.wipeOut();
		$('#pbox-text').empty();
		$('#pbox').hide();
	    },

	},

	selectCategory: function (id) {
	    $('.ui-el-category').removeClass('selected');
	    $('.ui-el-top-category').removeClass('selected');
	    $('#'+id).addClass('selected');
	    Genesis.UI.closePopovers();
	    Genesis.query('/handle/category/click/' + id);
	    return false;
	},

	showWarning: function (text, btnid, cls) {
	    Genesis.UI.showAsModal('warningbox');
	    $('#warning-text').html(text);
	    $('#warningbox').addClass('modal');
	    warning_button_id = btnid;
	    if (typeof cls === "undefined") {
		warning_class = 'button';
	    } else {
		warning_class = cls;
	    };
	    $('.warning-button').unbind('click');
	    $('.warning-button').click(Genesis.acceptWarning);
	    $('#warning-cancel-button').click(Genesis.cancelWarning);
	    return false;
	},

	cancelWarning: function () {
	    Genesis.UI.hideModal('warningbox');
	    return false;
	},

	acceptWarning: function () {
	    Genesis.cancelWarning();
	    Genesis.query('/handle/'+ warning_class +'/click/' + warning_button_id);
	    return false;
	},

	UI: {
	    showAsModal: function (id) {
		$('#'+id+'-backdrop').fadeTo(500, 0, function () {
		    $(this).remove();
		});
		var backdrop = $('<div class="modal-backdrop" />')
		    .css('opacity', 0)
		    .appendTo(document.body)
		    .fadeTo(500, 0.5)
		    .attr('id', id+'-backdrop');
		$('#'+id)
		    .css('opacity', 0)
		    .appendTo(document.body)
		    .show()
		    .fadeTo(500, 1)
		    .center();
                firstPasswordEntry = true;
	    },

	    hideModal: function (id, remove) {
		if ($('#'+id).css('opacity') > 0)
		    $('#'+id).fadeTo(500, 0, function () {
			if (remove) $(this).remove(); else $(this).hide();
		    });
		$('#'+id+'-backdrop').fadeTo(500, 0, function () {
		    if (remove) $(this).remove(); else $(this).hide();
		});
	    },
		
	    popoverEvent: null,

	    prepPopover: function (event, id) {
		$('#'+id).toggleClass('selected');
		if(Genesis.UI.popoverEvent != null) { document.removeEventListener(Genesis.UI.popoverEvent);}
		Genesis.UI.popoverEvent = document.attachEventListener('click',Genesis.UI.closePopovers);
		Genesis.UI.closeOtherPopovers(id);
		event.stopPropagation();
	    },

	    closePopovers: function () {
		$('.pop-trigger').popover('hide');
		$('.pop-trigger').removeClass('selected');
		$('.popover').css('display', 'none');
                $(document).off('click.popover.close');
	    },

	    closeOtherPopovers: function (id) {
		$('.pop-trigger').each(function (i) {
		    if ( this.id != id ) {
			$('#'+this.id).popover('hide');
			$('.popover').css('display', 'none');
			$('#'+this.id).removeClass('selected');
		    }
		});
	    },

	    showLoader: function (visible) {
		if (visible) {
		    $('#whiteout').show().fadeTo(3000, 1);
		    $('#ajax-loader').show().fadeTo(500, 1);
		    $('body').css('cursor', 'wait !important');
		}
		else {
		    $('#whiteout').stop().fadeTo(250, 0, function () { $(this).hide() });
		    $('#ajax-loader').stop().fadeTo(250, 0, function () { $(this).hide() });
		    $('#ajax-data').text('');
		    $('body').css('cursor', '');
		}
	    },

	    wipeOut: function (visible) {
		if (visible) {
		    $('#whiteout').show().fadeTo(200, 1);
		    $('body').css('cursor', 'wait !important');
		}
		else {
		    $('#whiteout').stop().fadeTo(250, 0, function () { $(this).hide() });
		    $('body').css('cursor', '');
		}
	    },

	    toggleTreeNode: function (id) {
		$('*[id=\''+id+'\']').toggle();
		Genesis.query('/handle/treecontainer/click/'+id, null, true);

		x = $('*[id=\''+id+'-btn\']');
		if (x.attr('src').indexOf('/dl/core/ui/tree-minus.png') < 0)
		    x.attr('src', '/dl/core/ui/tree-minus.png');
		else
		    x.attr('src', '/dl/core/ui/tree-plus.png');

		return false;
	    },

	    editableActivate: function (id) {
		function applyActivation(id){
		    $('#'+id+'-normal').hide();
		    $('#'+id).fadeIn(600);
		}
		if(typeof id === 'string'){
		    applyActivation(id);
		} else { // Input is an array
		    for(var i = 0; i < id.length; i++){
			applyActivation(id[i]);
		    }	
		}
		return false;
	    },
	}
    };
}());

jQuery.fn.center = function () {
    this.css("top", (
        Math.max(
            ($(window).height() - this.outerHeight()) / 2,
            0
        ) + $(window).scrollTop()
    ) + "px");

    this.css("left", Math.max(0,(($(window).width() - this.outerWidth()) / 2) + $(window).scrollLeft()) + "px");
    return this;
}


function noenter() {
    return !(window.event && window.event.keyCode == 13);
}

function ui_fill_custom_html(id, html) {
    document.getElementById(id).innerHTML = Base64.decode(html);
}
