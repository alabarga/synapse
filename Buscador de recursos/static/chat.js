$(document).ready(function() {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};

    $("#messageform").live("submit", function() {
        newMessage($(this));
        return false;
    });
    $("#messageform").live("keypress", function(e) {
        if (e.keyCode == 13) {
            newMessage($(this));
            return false;
        }
    });
    $("#message").select();
    updater.start();
    
});

$(window).unload(function() {
    updater.stop()
});

function newMessage(form) {
    var message = form.formToDict();
    updater.socket.send(JSON.stringify(message));
    form.find("input[type=text]").val("");
    $("input:checkbox").attr('checked', false);
}

jQuery.fn.formToDict = function() {
    var fields = this.serializeArray();
    var json = {}
    for (var i = 0; i < fields.length; i++) {
        json[fields[i].name] = fields[i].value;
    }
    if (json.next) delete json.next;
    return json;
};

var updater = {
    socket: null,

    start: function() {
        if ("WebSocket" in window) {
	       updater.socket = new WebSocket("ws://localhost:8888/realtime");
        } else {
            updater.socket = new MozWebSocket("ws://localhost:8888/realtime");
        }
    	updater.socket.onmessage = function(event) {
            console.log(event.data);
    	    updater.showMessage(JSON.parse(event.data));
    	}
    },

    stop: function() {
        updater.socket.close();
        updater.socket = null;
    },

    showMessage: function(node) {
        var existing = $("#m" + node.id);
        if (existing.length > 0) return;
        var node = $(node.html);
        node.hide();
        console.log(node.html);
        $("#inbox").prepend(node);      
        setTimeout(function() { node.slideDown();}, 8000);
        if($("#inbox").children().length>20){
            $("#inbox div").filter(":last").remove();
        }
        $.embedly.defaults.key = 'cf79042ab7ee4ffca91e17e7ab0aac10';
        $(existing).display('crop', {
            query: {
              width:100,
              height:100,
              grow:true
            }
        });
    }
};
