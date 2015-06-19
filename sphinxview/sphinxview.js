// Copyright 2015 Troels Brødsgaard
// License: 2-clause BSD, see LICENSE for details

$(document).ready(function() {
    var url = '/polling?build_file=' + location.pathname;
    $.ajax(url, {
        type: 'HEAD',
        success: function(response) {
            var base_url = window.location.href.split('?')[0]
            var scroll = $(document).scrollTop();
            window.location.href = base_url + '?scroll=' + scroll;
        }
    });
    if (window.location.href.indexOf('scroll') != -1) {
        var scroll = window.location.href.split('=')[1];
        $(document).scrollTop(scroll)
    }
});

