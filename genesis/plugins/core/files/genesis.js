var Genesis;

var warning_button_id;

Genesis = {
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
        Genesis.UI.animateProgress();
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
                    clearTimeout(Genesis.UI._animateProgressTimeout);
                    for (prg in j) {
                        Genesis.Core.addProgress(j[prg]);
                    }
                    Genesis.UI.animateProgress();
                },
                complete: function () {
                    setTimeout('Genesis.Core.requestProgress()', 3000);
                }
            });
        },

        addProgress: function (desc) {
            var html = '<div class="progress-box"><a class="close" onclick="return Genesis.showWarning(\'';
            html += 'Cancel background task for ' + desc.owner + '?\', \'aborttask/' + desc.id + '\');">×</a>';
            html += '<p><strong>' + desc.owner + '</strong> ' + desc.status + '</p></div>';
            $('#progress-box').append(html);
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

    showWarning: function (text, btnid) {
        Genesis.UI.showAsModal('warningbox');
        $('#warning-text').html(text);
        $('#warningbox').addClass('modal');
        warning_button_id = btnid;
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
        Genesis.query('/handle/button/click/' + warning_button_id);
        return false;
    },

    UI: {
        showAsModal: function (id) {
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

        prepPopover: function (id) {
            $('#'+id).toggleClass('selected');
            Genesis.UI.closeOtherPopovers(id);
        },

        closePopovers: function () {
            $('.pop-trigger').popover('hide');
            $('.pop-trigger').removeClass('selected');
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
            $('#'+id+'-normal').hide();
            $('#'+id).fadeIn(600);
            return false;
        },

        _animateProgressTimeout: null, 

        animateProgress: function () {
            var x = $('.progress-box').css('background-position-x');
            if (!x || x.length < 3) x = '0px';
            x = x.substr(0, x.length - 2);
            x = parseInt(x);
            $('.progress-box').css('background-position-x', x);
            $('.progress-box').stop().animate(
                {'background-position-x': x + 100}, 
                1000, 
                'linear'
            );
            Genesis.UI._animateProgressTimeout = setTimeout('Genesis.UI.animateProgress()', 1000);
        },
    }
};



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
