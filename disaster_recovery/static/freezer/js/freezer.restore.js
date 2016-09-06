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


function get_url() {
  var url = Browser.get_url();
  url += 'clients/';
  return url;
}

function freezerGetRow(item) {
  var tr = $('<tr>');
  tr.append($('<td class="multi_select_column">')
    .append($('<input type="radio" name="client">')
      .attr('value', item.client.client_id)));
  tr.append($('<td>').text(item.client.hostname));
  return tr;
}

$.ajax({
    url: get_url(),
    type: "GET",
    cache: false,
    dataType: 'json',
    contentType: 'application/json; charset=utf-8',
    success: function(data) {
        $.each(data, function (index, item) {
            $("#available_clients").append(freezerGetRow(item));
        });
    },
    error: function (request, error) {
        $("#available_clients").append(
            '<tr><td>Error getting client list</td></tr>' // UNTRANSLATED
        );
    }
});

