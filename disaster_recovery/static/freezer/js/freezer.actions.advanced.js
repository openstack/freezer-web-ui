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

$("#id_no_incremental").click(function () {
    if ($("#id_no_incremental").is(":checked")) {
        $("#id_max_level").closest(".form-group").hide();
        $("#id_always_level").closest(".form-group").hide();
        $("#id_restart_always_level").closest(".form-group").hide();
    } else {
        $("#id_max_level").closest(".form-group").show();
        $("#id_always_level").closest(".form-group").show();
        $("#id_restart_always_level").closest(".form-group").show();
    }
});