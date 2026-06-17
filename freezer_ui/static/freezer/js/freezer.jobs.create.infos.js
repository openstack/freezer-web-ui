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

function initJobsCreateInfos() {
    var $intervalUint = $("#id_interval_uint");

    if (!$intervalUint.length || $intervalUint.data('freezer-initialized')) {
        return;
    }
    $intervalUint.data('freezer-initialized', true);

    function showIntervalValue() {
        $("#id_interval_value").closest(".form-group").show();
    }

    function hideIntervalValue() {
        $("#id_interval_value").closest(".form-group").hide();
    }

    $intervalUint.change(function () {
        var interval_uint_val = $intervalUint.val();
        if (interval_uint_val !== 'continuous') {
            showIntervalValue();
        } else {
            hideIntervalValue();
        }
    });

    hideIntervalValue();
}

if (typeof horizon !== 'undefined') {
    horizon.addInitFunction(function () {
        initJobsCreateInfos();
    });
} else {
    $(function () {
        initJobsCreateInfos();
    });
}

$(document).on("show.bs.modal", ".modal", function () {
    initJobsCreateInfos();
});
