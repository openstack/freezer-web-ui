/*global $, location*/

'use strict';


$(function () {
    var $sortableLists = $(".sortable_lists");
    if (!$sortableLists.length) {
        return;
    }
    $("#actions_available, #actions_selected").sortable({
        connectWith: ".connectedSortable"
    }).disableSelection();

    var $parentContainer = $sortableLists.parent();
    $parentContainer.removeClass("col-sm-6").addClass("col-sm-12");
    $parentContainer.siblings().hide();

    $sortableLists.closest("form").submit(function (event) {
        var selectedIds = $("#actions_selected li").map(function () {
            return $(this).attr('id');
        }).get();
        var idString = selectedIds.join('===');
        if (idString) { idString += '==='; }
        $('#id_actions').val(idString);
    });
});
