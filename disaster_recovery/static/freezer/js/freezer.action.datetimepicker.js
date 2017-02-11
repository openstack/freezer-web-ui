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

/*global $*/

"use strict";

$(function () {
    var config = {
        format: 'YYYY-MM-DDTHH:mm:ss',
        icons: {
            time: 'fa fa-clock-o',
            date: 'fa fa-calendar',
            up: 'fa fa-chevron-up',
            down: 'fa fa-chevron-down',
            previous: 'fa fa-chevron-left',
            next: 'fa fa-chevron-right',
            today: 'fa fa-circle-o',
            clear: 'fa fa-trash',
            close: 'fa fa-times'
        },
        showClose: true,
        tooltips: {
            today: 'Go to today',
            clear: 'Clear selection',
            close: 'Close the picker'
        },
        widgetPositioning: {
            horizontal: 'left',
            vertical: 'bottom'
        }
    };

    var $restore_from_date = $("#id_restore_from_date");
    $restore_from_date.datetimepicker(config);

    var $remove_from_date = $("#id_remove_from_date");
    $remove_from_date.datetimepicker(config);

});
