function showStuff() {
  var req = new XMLHttpRequest();
  req.open("GET", "/latest", true);
  req.onreadystatechange = function() {
    if (req.readyState != 4) {
      return;
    }
    gotStuff(req.status, req.responseText);
  };
  req.send(null);
}

function gotStuff(status, text) {
  if (status != 200) {
    window.setTimeout(showStuff, 5000);
    return;
  }

  var content = text;
  document.getElementById("content").innerHTML = content;
  window.setTimeout(showStuff, 1000);
}

window.onload = showStuff;
