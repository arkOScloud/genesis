$(document).on('sortstart', '.dashboard', function () {
    $('#trash').fadeTo(500, 1);
});

$(document).on('sortstop', '.dashboard', function () {
    $('#trash').fadeTo(500, 0).empty().text('Drop here to remove widget');
    $('#save-query').show();
    $('#save-query').animate({'height':'50px'}, 1000);
});

function dashboardSave() {
    var l = '';
    var r = '';

    $('#cleft > *').each(function(i,e) {
        l += $(e).attr('id') + ',';
    });
    $('#cright > *').each(function(i,e) {
        r += $(e).attr('id') + ',';
    });

    Genesis.query('/handle/sysmon/save/'+l+'/'+r);
    return false;
}
