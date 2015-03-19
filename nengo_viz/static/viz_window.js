/*This detects if the mouse has exited the browser window to prevent erratic behaviour upon re-entry*/

function addEvent(obj, evt, fn) {
    if (obj.addEventListener) {
        obj.addEventListener(evt, fn, false);
    }
    else if (obj.attachEvent) {
        obj.attachEvent("on" + evt, fn);
    }
}

var main = document.getElementById('main');
addEvent(window,"load",function(e) {
    addEvent(main, "mouseout", function(e) {
        e = e ? e : window.event;
        var from = e.relatedTarget || e.toElement;
        if (!from || from.nodeName == "HTML") {
            $(main).trigger('mouseup');
        }
    });
});