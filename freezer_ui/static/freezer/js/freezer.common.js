var Browser = (function () {

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
        }
    }

})();
