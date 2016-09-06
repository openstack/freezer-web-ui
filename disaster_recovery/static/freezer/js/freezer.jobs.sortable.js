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


var job_id = $('#id_job_id').val();


function actions_in_job_url() {
  var url = Browser.get_url();
  url += 'actions/job/';
  url += job_id;
  return url;
}


function actions_url() {
  var url = Browser.get_url();
  url += 'actions/';
  return url;
}

function freezerLi(item) {
  return $('<li class="list-group-item">')
    .attr('id', item.action_id)
    .text("(" + item.freezer_action.action + ") " + item.freezer_action.backup_name);
}

if (job_id !== "") {
    $.ajax({
        url: actions_in_job_url(),
        type: "GET",
        cache: false,
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        success: function (data) {
            $.each(data.available, function (index, item) {
                $("#actions_available").append(freezerLi(item));
            });
            $.each(data.selected, function (index, item) {
                $("#actions_selected").append(freezerLi(item));
            });
        },
        error: function (request, error) {
            $("#actions_available").append(
                '<tr><td>Error getting action list</td></tr>' // UNTRANSLATED
            );
        }
    });
} else {
    $.ajax({
        url: actions_url(),
        type: "GET",
        cache: false,
        dataType: 'json',
        contentType: 'application/json; charset=utf-8' ,
        success: function (data) {
            $.each(data, function (index, item) {
                $("#actions_available").append(freezerLi(item));
            });
        },
        error: function (request, error) {
            $("#actions_available").append(
                '<tr><td>Error getting action list</td></tr>' // UNTRANSLATED
            );
        }
    });
}
