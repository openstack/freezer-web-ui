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
    $("#id_restore_abs_path").closest(".form-group").show();
    $("#id_restore_from_host").closest(".form-group").show();
    $("#id_restore_from_date").closest(".form-group").show();
    $("#id_storage").closest(".form-group").show();
}

function showSSHOptions() {
    $("#id_ssh_key").closest(".form-group").show();
    $("#id_ssh_username").closest(".form-group").show();
    $("#id_ssh_host").closest(".form-group").show();
}

function triggerChanges() {
    $("#id_action").trigger('change');
    $("#id_mode").trigger('change');
    $("#id_storage").trigger('change');
}

function hideModeOptions() {
    $("#id_cinder_vol_id").closest(".form-group").hide();
    $("#id_nova_inst_id").closest(".form-group").hide();
    $("#id_mysql_conf").closest(".form-group").hide();
    $("#id_sql_server_conf").closest(".form-group").hide();
}

function hideSSHOptions() {
    $("#id_ssh_key").closest(".form-group").hide();
    $("#id_ssh_username").closest(".form-group").hide();
    $("#id_ssh_host").closest(".form-group").hide();
}

$("#id_action").change(function () {
    // Update the inputs according freezer action
    if ($("#id_action").val() === 'backup') {
        hideEverything();
        showBackupOptions();
    } else if ($("#id_action").val() === 'restore') {
        hideEverything();
        showRestoreOptions();
    } else if ($("#id_action").val() === 'admin') {
        hideEverything();
        showAdminOptions();
    } else {
        hideEverything();
    }
});


$("#id_storage").change(function () {
    // Update the inputs according freezer storage backend
    if ($("#id_storage").val() === 'swift') {
        //hideEverything();
        showBackupOptions();
        hideSSHOptions();
    } else if ($("#id_storage").val() === 'ssh') {
        //hideEverything();
        showBackupOptions();
        showSSHOptions();
    } else if ($("#id_storage").val() === 'local') {
        //hideEverything();
        showBackupOptions();
        hideSSHOptions();
    }
});


$("#id_mode").change(function () {
    // Update the inputs according freezer mode
    if ($("#id_action").val() === 'backup') {
        if ($("#id_mode").val() === 'fs') {
            hideModeOptions();
        } else if ($("#id_mode").val() === 'mysql') {
            hideModeOptions();
            $("#id_mysql_conf").closest(".form-group").show();
        } else if ($("#id_mode").val() === 'mssql') {
            hideModeOptions();
            $("#id_sql_server_conf").closest(".form-group").show();
        } else if ($("#id_mode").val() === 'mongo') {
            hideModeOptions();
        } else if ($("#id_mode").val() === 'cinder') {
            hideModeOptions();
            $("#id_cinder_vol_id").closest(".form-group").show();
        } else if ($("#id_mode").val() === 'nova') {
            hideModeOptions();
            $("#id_nova_inst_id").closest(".form-group").show();
        }
    }
});


$(function () {
    hideEverything();
    triggerChanges();
});