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

function hideOptions() {
    // Snapshot specific controls
    $("#id_is_windows").closest(".form-group").hide();
    $("#id_lvm_auto_snap").closest(".form-group").hide();
    $("#id_lvm_srcvol").closest(".form-group").hide();
    $("#id_lvm_snapname").closest(".form-group").hide();
    $("#id_lvm_snapsize").closest(".form-group").hide();
    $("#id_lvm_dirmount").closest(".form-group").hide();
    $("#id_lvm_volgroup").closest(".form-group").hide();
}

function is_windows() {
    if ($("#id_is_windows").is(":checked")) {
        return true;
    }
}

function showWindowsSnapshotOptions() {
    $("#id_vssadmin").closest(".form-group").show();
}

function showLinuxSnapshotOptions() {
    $("#id_lvm_auto_snap").closest(".form-group").show();
    $("#id_lvm_srcvol").closest(".form-group").show();
    $("#id_lvm_snapname").closest(".form-group").show();
    $("#id_lvm_snapsize").closest(".form-group").show();
    $("#id_lvm_dirmount").closest(".form-group").show();
    $("#id_lvm_volgroup").closest(".form-group").show();
}

function hideLinuxSnapshotOptions() {
    $("#id_lvm_srcvol").closest(".form-group").hide();
    $("#id_lvm_snapname").closest(".form-group").hide();
    $("#id_lvm_snapsize").closest(".form-group").hide();
    $("#id_lvm_dirmount").closest(".form-group").hide();
    $("#id_lvm_volgroup").closest(".form-group").hide();
    $("#id_lvm_auto_snap").closest(".form-group").hide();
}

function hideSnapshotOptions() {
    hideLinuxSnapshotOptions();
    $("#id_is_windows").closest(".form-group").hide();
}

function showSnapshotOptions() {
    $("#id_is_windows").closest(".form-group").show();
    if (is_windows()) {
        hideLinuxSnapshotOptions();
        showWindowsSnapshotOptions();
    } else {
        showLinuxSnapshotOptions();
    }
}

hideOptions();

$("#id_use_snapshot").click(function () {
    if ($("#id_use_snapshot").is(":checked")) {
        showSnapshotOptions();
    } else {
        hideSnapshotOptions();
    }
});

$("#id_is_windows").click(function () {
    if ($("#id_use_snapshot").is(":checked")) {
        showSnapshotOptions();
    } else {
        hideSnapshotOptions();
    }
});