var page = require('webpage').create();
var system = require('system')

var url = system.args[1];
var filename = system.args[2];
page.viewportSize = { width: 1024, height: 768 };
page.clipRect = { top: 0, left: 0, width: 1024, height: 768 };
page.settings.resourceTimeout = parseInt(system.args[3])

page.onResourceTimeout = function(request) {
    phantom.exit(1);
};

page.open(url, function(status) {
    if (status !== 'success') {
        phantom.exit(1)
    } else {
        window.setTimeout(function() {
            page.render(filename);
            phantom.exit(0);
        }, 500);
    }
});
