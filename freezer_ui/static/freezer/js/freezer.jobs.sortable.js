/*
# (c) Copyright 2014,2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
*/

/*global $, location*/

"use strict";

$(function () {
    $("#sortable1, #sortable2").sortable({
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
    $("#sortable2 li").each(function (index) {
        ids += ($(this).attr('id'));
        ids += "===";
    });
    $('#id_actions').val(ids);
});


function get_actions_url() {
    var url = $(location).attr("origin");
    url += '/freezer_ui/api/actions';
    return url;
}

var job_id = $('#id_original_name').val();

if (job_id !== "") {
    var url_available = get_actions_url();

    $.ajax({
        url: url_available,
        type: "GET",
        cache: false,
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        success: function (data) {
            $.each(data, function (index, item) {
                $("#sortable1").append(
                    "<li class='list-group-item' id=" + item.action_id + ">" +
                        item.freezer_action.backup_name + "</li>"
                );
            });
        },
        error: function (request, error) {
            $("#sortable1").append(
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
                $("#sortable1").append(
                    "<li class='list-group-item' id=" + item.action_id + ">" +
                        item.freezer_action.backup_name +
                        "</li>"
                );
            });
        },
        error: function (request, error) {
            $("#sortable1").append(
                '<tr><td>Error getting action list</td></tr>'
            );
        }
    });
}