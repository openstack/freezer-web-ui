var freezerBrowser = (function () {
    'use strict';

    var url = null;
    var webroot = '/';
    if (typeof WEBROOT !== 'undefined') {
        webroot = WEBROOT;
    } else if (typeof window.WEBROOT !== 'undefined') {
        webroot = window.WEBROOT;
    } else if (typeof horizon !== 'undefined' && typeof horizon.conf !== 'undefined' && typeof horizon.conf.webroot !== 'undefined') {
        webroot = horizon.conf.webroot;
    }

    url = webroot + 'project/freezer-api/';

    return {
        get_url : function () {
            return url;
        },
        get_webroot: function () {
            return webroot;
        }
    };

})();

$(function () {
    'use strict';
    // Sync active tab to URL search parameter
    $(document).on('shown.bs.tab', 'a[data-toggle="tab"]', function (e) {
        var tabName = $(e.target).attr('href').substring(1);
        var url = new URL(window.location);
        url.searchParams.set('tab', tabName);
        window.history.replaceState({}, '', url);
    });
});

