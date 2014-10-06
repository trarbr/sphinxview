// Copyright 2014 Troels Brødsgaard
// License: 2-clause BSD, see LICENSE for details

$(document).ready(function () {
  var xmlHttp = null;
  setTimeout(function () {
    if (window.XMLHttpRequest) {
      xmlHttp = new XMLHttpRequest();
    } else if (window.ActiveXObject) {
      xmlHttp = new ActiveXObject('Microsoft.XMLHTTP');
    }
    xmlHttp.onreadystatechange = function () {
      if (xmlHttp.readyState == 4 && xmlHttp.status == '200') {
        window.location.reload(true);
      }
    }
    xmlHttp.open('HEAD', '/polling?build_file=' + location.pathname, true);
    xmlHttp.send(null);
  }, 0);
});
