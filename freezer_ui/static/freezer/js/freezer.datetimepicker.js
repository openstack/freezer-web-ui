/*global $*/

"use strict";

$(function () {
    $('#id_schedule_start_date').datetimepicker({
        format: 'YYYY-MM-DDTHH:mm:ss'
    });

    $('#id_schedule_end_date').datetimepicker({
        format: 'YYYY-MM-DDTHH:mm:ss'
    });
});
