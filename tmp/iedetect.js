
var hasIE_phone_home = 0;


// This function does the actual browser detection
function hasIE_hasIE() {
  var ua = navigator.userAgent.toLowerCase();
  return ((ua.indexOf('msie') != -1) && (ua.indexOf('opera') == -1) && 
          (ua.indexOf('webtv') == -1) && (ua.indexOf('msie 7.0') == -1) &&
          (location.href.indexOf('seenIEPage') == -1));
}

function hasIE_showOnlyLayer(whichLayer)
{
  if (document.getElementById)
    {
      var style2 = document.getElementById(whichLayer);
    }
  else if (document.all)
    {
      var style2 = document.all[whichLayer];
    }
  else if (document.layers)
    {
      var style2 = document.layers[whichLayer];
    }
  var body = document.getElementsByTagName('body');
  body[0].innerHTML = style2.innerHTML;
}

function hasIE_showLayer(whichLayer)
{
  if (document.getElementById)
    {
      var style2 = document.getElementById(whichLayer).style;
      style2.display = "block";
    }
  else if (document.all)
    {
      var style2 = document.all[whichLayer].style;
      style2.display = "block";
    }
  else if (document.layers)
    {
      var style2 = document.layers[whichLayer].style;
      style2.display = "block";
    }
}

// Hides and shows sections of the page based on whether or not it's
// running in IE
function hasIE_hideAndShow() {
  if (hasIE_hasIE()) {
    hasIE_showLayer("hasIE_level1");
  }
}

