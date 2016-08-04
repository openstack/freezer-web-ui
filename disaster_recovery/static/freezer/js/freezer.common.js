var Browser = (function () {

    var url = null;
    url = $(location).attr("protocol");
    url += "//";
    url += $(location).attr("host");

    url += WEBROOT + 'disaster_recovery/api/';

    return {
        get_url : function () {
            return url;
        }
    }

})();
