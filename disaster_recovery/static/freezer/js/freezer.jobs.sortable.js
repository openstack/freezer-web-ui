/*global $, location*/

'use strict';


$(function () {
    $("#actions_available, #actions_selected").sortable({
        connectWith: ".connectedSortable"
    }).disableSelection();
});


var parent = $(".sortable_lists").parent();
parent.removeClass("col-sm-6");
parent.addClass("col-sm-12");
var siblings = parent.siblings();
siblings.remove();


$("form").submit(function (event) {
    var ids = "";
    $("#actions_selected li").each(function (index) {
        ids += ($(this).attr('id'));
        ids += "===";
    });
    $('#id_actions').val(ids);
});


var job_id = $('#id_job_id').val();

function get_url() {
    var url = $(location).attr("origin");
    url += '/disaster_recovery/api/actions/job/';
    url += job_id;
    return url;
}

function get_actions_url() {
    var url = $(location).attr("origin");
    url += '/disaster_recovery/api/actions';
    return url;
}

if (job_id !== "") {
    $.ajax({
        url: get_url(),
        type: "GET",
        cache: false,
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        success: function (data) {
            $.each(data.available, function (index, item) {
                $("#actions_available").append(
                    "<li class='list-group-item' id=" + item.action_id + ">" +
                        item.freezer_action.backup_name + "</li>"
                );
            });
            $.each(data.selected, function (index, item) {
                $("#actions_selected").append(
                    "<li class='list-group-item' id=" + item.action_id + ">" +
                        item.freezer_action.backup_name + "</li>"
                );
            });
        },
        error: function (request, error) {
            $("#actions_available").append(
                '<tr><td>Error getting action list</td></tr>'
            );
        }
    });
} else {
    var url = get_actions_url();

    $.ajax({
        url: url,
        type: "GET",
        cache: false,
        dataType: 'json',
        contentType: 'application/json; charset=utf-8' ,
        success: function (data) {
            $.each(data, function (index, item) {
                $("#actions_available").append(
                    "<li class='list-group-item' id=" + item.action_id + ">" +
                        item.freezer_action.backup_name +
                        "</li>"
                );
            });
        },
        error: function (request, error) {
            $("#actions_available").append(
                '<tr><td>Error getting action list</td></tr>'
            );
        }
    });
}