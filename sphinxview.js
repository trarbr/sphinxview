var xmlHttp = null;
window.onload = function () {
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
    var footer = document.getElementsByClassName("footer");
    var last_updated = elements[0].innerHTML;
    xmlHttp.open('HEAD', '/polling?pathname=' + location.pathname + '&mtime=%d', true);
    xmlHttp.open('HEAD', '/polling?build_file=' + location.pathname + '&last_updated=' + last_updated, true);
    xmlHttp.send(null);
  }, 0);
}

window.onbeforeunload = function () {
   xmlHttp.abort();
}