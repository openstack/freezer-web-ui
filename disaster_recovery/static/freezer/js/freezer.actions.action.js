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

function hideEverything() {
    // Common controls
    $("#id_backup_name").closest(".form-group").hide();
    $("#id_container").closest(".form-group").hide();
    $("#id_path_to_backup").closest(".form-group").hide();
    $("#id_storage").closest(".form-group").hide();

    // Backup specific controls
    $("#id_mysql_conf").closest(".form-group").hide();
    $("#id_mode").closest(".form-group").hide();
    $("#id_sql_server_conf").closest(".form-group").hide();
    $("#id_cinder_vol_id").closest(".form-group").hide();
    $("#id_nova_inst_id").closest(".form-group").hide();

    // Restore specific controls
    $("#id_restore_abs_path").closest(".form-group").hide();
    $("#id_restore_from_host").closest(".form-group").hide();
    $("#id_restore_from_date").closest(".form-group").hide();
    $("#restore-warning").hide();
    $("#id_nova_restore_network").closest(".form-group").hide();

    // Admin specific controls
    $("#id_remove_older_than").closest(".form-group").hide();
    $("#id_remove_from_date").closest(".form-group").hide();
    $("#id_get_object").closest(".form-group").hide();
    $("#id_dst_file").closest(".form-group").hide();

    // SSH specific controls
    $("#id_ssh_key").closest(".form-group").hide();
    $("#id_ssh_username").closest(".form-group").hide();
    $("#id_ssh_host").closest(".form-group").hide();

}

function showAdminOptions() {
    $("#id_remove_older_than").closest(".form-group").show();
    $("#id_remove_from_date").closest(".form-group").show();
    $("#id_get_object").closest(".form-group").show();
    $("#id_dst_file").closest(".form-group").show();
}

function showBackupOptions() {
    $("#id_is_windows").closest(".form-group").show();
    $("#id_mode").closest(".form-group").show();
    $("#id_container").closest(".form-group").show();
    $("#id_path_to_backup").closest(".form-group").show();
    $("#id_backup_name").closest(".form-group").show();
    $("#id_storage").closest(".form-group").show();
}

function showRestoreOptions() {
    $("#id_container").closest(".form-group").show();
    $("#id_backup_name").closest(".form-group").show();
    $("#id_mode").closest(".form-group").show();
    $("#id_restore_abs_path").closest(".form-group").show();
    $("#id_restore_from_host").closest(".form-group").show();
    $("#id_restore_from_date").closest(".form-group").show();
    $("#id_storage").closest(".form-group").show();
    $("#restore-warning").show();
}

function showSSHOptions() {
    $("#id_ssh_key").closest(".form-group").show();
    $("#id_ssh_username").closest(".form-group").show();
    $("#id_ssh_host").closest(".form-group").show();
}

function setActionOptions() {
    // Update the inputs according freezer action
    var $id_action = $("#id_action").val();
    if ($id_action === 'backup') {
        showBackupOptions();
    } else if ($id_action === 'restore') {
        showRestoreOptions();
    } else if ($id_action === 'admin') {
        showAdminOptions();
    }
}

function setStorageOptions() {
    // Update the inputs according freezer storage backend
    var $id_action = $("#id_action").val();
    if ($id_action === 'backup' || $id_action === 'restore') {
        if ($("#id_storage").val() === 'ssh') {
            showSSHOptions();
        }
    }
}

function setModeOptions() {
    var $id_mode = $("#id_mode").val();
    // Update the inputs according freezer mode
    if ($("#id_action").val() === 'backup') {
        if ($id_mode === 'mysql') {
            $("#id_mysql_conf").closest(".form-group").show();
        } else if ($id_mode === 'mssql') {
            $("#id_sql_server_conf").closest(".form-group").show();
        } else if ($id_mode === 'cinder') {
            $("#id_cinder_vol_id").closest(".form-group").show();
            $("#id_path_to_backup").closest(".form-group").hide();
        } else if ($id_mode === 'nova') {
            $("#id_nova_inst_id").closest(".form-group").show();
            $("#id_path_to_backup").closest(".form-group").hide();
        }
    } else if($("#id_action").val() === 'restore') {
        if ($id_mode === 'mysql') {
            $("#id_mysql_conf").closest(".form-group").show();
        } else if ($id_mode === 'mssql') {
            $("#id_sql_server_conf").closest(".form-group").show();
        } else if ($id_mode === 'cinder') {
            $("#id_cinder_vol_id").closest(".form-group").show();
        } else if ($id_mode === 'nova') {
            $("#id_nova_inst_id").closest(".form-group").show();
            $("#id_nova_restore_network").closest(".form-group").show();
        }
    }
}

$("#id_action, #id_storage, #id_mode").change(function () {
    hideEverything();
    setActionOptions();
    setStorageOptions();
    setModeOptions();
});

$(function () {
    hideEverything();
    setActionOptions();
    setStorageOptions();
    setModeOptions();
});
