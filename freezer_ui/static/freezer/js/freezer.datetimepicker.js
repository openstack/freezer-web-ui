/*global $*/

"use strict";

$(function () {
    $('#id_schedule_start_date').datetimepicker({
        format: 'YYYY-MM-DDThh:mm:ss'
    });

    $('#id_schedule_end_date').datetimepicker({
        format: 'YYYY-MM-DDThh:mm:ss'
    });
});
