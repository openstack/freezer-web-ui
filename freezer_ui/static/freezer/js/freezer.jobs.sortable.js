/*global $, location*/

'use strict';


$(function () {
    $("#actions_available, #actions_selected").sortable({
        connectWith: ".connectedSortable"
    }).disableSelection();
});

// BAD: This is putting all these members on global scope.

var parent = $(".sortable_lists").parent();
parent.removeClass("col-sm-6");
parent.addClass("col-sm-12");
var siblings = parent.siblings();
siblings.hide();


$("form").submit(function (event) {
    var ids = "";
    $("#actions_selected li").each(function (index) {
        ids += ($(this).attr('id'));
        ids += "===";
    });
    $('#id_actions').val(ids);
});
