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
    $('#id_schedule_start_date').datetimepicker({
        format: 'YYYY-MM-DDTHH:mm:ss',
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
    });

    $('#id_schedule_end_date').datetimepicker({
        format: 'YYYY-MM-DDTHH:mm:ss',
        showClose: true,
        tooltips: {
            today: 'Go to today',
            clear: 'Clear selection',
            close: 'Close the picker'
        },
        widgetPositioning: {
            horizontal: 'left',
            vertical: 'bottom'
        },
        useCurrent: false //Important! See issue #1075
    });

    $("#id_schedule_start_date").on("dp.change", function (e) {
        $('#id_schedule_end_date').data("DateTimePicker").minDate(e.date);
    });
    $("#id_schedule_end_date").on("dp.change", function (e) {
        $('#id_schedule_start_date').data("DateTimePicker").maxDate(e.date);
    });
});
