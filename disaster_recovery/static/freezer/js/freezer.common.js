var Browser = (function () {

    var url_path = $(location).attr("pathname");

    var url = null;
    url = $(location).attr("protocol");
    url += "//";
    url += $(location).attr("host");

    if (url_path.indexOf("horizon") > -1) {
        url += '/horizon/disaster_recovery/api/';
    } else {
        url += '/disaster_recovery/api/';
    }

    return {
        get_url : function () {
            return url;
        }
    }

})();
