// Copyright 2015 Troels Brødsgaard
// License: 2-clause BSD, see LICENSE for details

$(document).ready(function() {
    var url = '/polling?build_file=' + location.pathname
    $.ajax(url, {
        type: 'HEAD',
        success: function(response) {
            window.location.reload(true);
        }
    });
});
