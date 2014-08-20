$(document).ready(function(){
  send_request();
});

function send_last_updated(){
  // recursion
  send_request();
  setInterval(send_last_updated, 2000);
}

function send_request(){
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
    var elements = document.getElementsByClassName("footer");
    var last_updated = elements[0].innerHTML;
    xmlHttp.open('HEAD', '/polling?file_path=' + location.pathname + '&last_updated=' + last_updated, true);
    xmlHttp.send(null);
    }, 0);
  }
