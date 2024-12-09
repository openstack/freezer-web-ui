var Browser = (function () {

    var url = null;
    url = $(location).attr("protocol");
    url += "//";
    url += $(location).attr("host");

    url += WEBROOT + 'freezer_ui/api/';

    return {
        get_url : function () {
            return url;
        }
    }

})();
