/*global $, location, Browser*/

'use strict';

var allClients = [];

function filterActions() {
    var selectedIds = [];
    $("#id_selected_clients_member option").each(function() {
        selectedIds.push($(this).val());
    });

    var selectedClients = [];
    if (selectedIds.length > 0 && allClients.length > 0) {
        $.each(allClients, function(i, c) {
            var uuid = c.uuid || (c.client && c.client.uuid) || c.client_id;
            if (selectedIds.indexOf(uuid) !== -1) {
                selectedClients.push(c.client || {});
            }
        });
    }

    $("#actions_available li, #actions_selected li").each(function() {
        var $li = $(this);
        var act = $li.attr('data-action');
        var mode = $li.attr('data-mode');
        var storage = $li.attr('data-storage');
        var engine = $li.attr('data-engine');

        var isCompatible = true;

        if (selectedClients.length > 0) {
            $.each(selectedClients, function(i, client) {
                if (act && client.supported_actions && client.supported_actions.length > 0 && client.supported_actions.indexOf(act) === -1) {
                    isCompatible = false;
                }
                if (mode && client.supported_modes && client.supported_modes.length > 0 && client.supported_modes.indexOf(mode) === -1) {
                    isCompatible = false;
                }
                if (storage && client.supported_storages && client.supported_storages.length > 0 && client.supported_storages.indexOf(storage) === -1) {
                    isCompatible = false;
                }
                if (engine && client.supported_engines && client.supported_engines.length > 0 && client.supported_engines.indexOf(engine) === -1) {
                    isCompatible = false;
                }
            });
        }

        var inSelected = $li.parent().attr('id') === 'actions_selected';

        if (isCompatible) {
            $li.show();
            if (inSelected) {
                $li.removeClass("list-group-item-danger");
                $li.find(".compat-warning").remove();
            }
        } else {
            if (inSelected) {
                $li.addClass("list-group-item-danger");
                if (!$li.find(".compat-warning").length) {
                    $li.append('<span class="label label-danger pull-right compat-warning" style="margin-top: 2px;">Incompatible with Client</span>');
                }
            } else {
                $li.hide();
            }
        }
    });
    checkPlaceholders();
}

function checkPlaceholders() {
    var $available = $("#actions_available");
    var $selected = $("#actions_selected");

    if ($available.length) {
        if ($available.children("li[id]").filter(function() { return this.style.display !== 'none'; }).length === 0) {
            if (!$available.children(".empty-placeholder").length) {
                $available.append('<li class="list-group-item empty-placeholder disabled text-muted" style="background-color: transparent; border-style: dashed; text-align: center;">No compatible actions available</li>');
            }
        } else {
            $available.children(".empty-placeholder").remove();
        }
    }

    if ($selected.length) {
        if ($selected.children("li[id]").length === 0) {
            if (!$selected.children(".empty-placeholder").length) {
                $selected.append('<li class="list-group-item empty-placeholder disabled text-muted" style="background-color: transparent; border-style: dashed; text-align: center;">No actions selected</li>');
            }
        } else {
            $selected.children(".empty-placeholder").remove();
        }
    }
}

function initJobsSortable() {
    var $sortableLists = $(".sortable_lists");
    if (!$sortableLists.length || $sortableLists.data('freezer-initialized')) {
        return;
    }
    $sortableLists.data('freezer-initialized', true);
    $("#actions_available, #actions_selected").sortable({
        connectWith: ".connectedSortable",
        items: "li:not(.empty-placeholder)",
        update: function (event, ui) {
            checkPlaceholders();
        }
    }).disableSelection();



    if (typeof window.allClients !== 'undefined') {
        allClients = window.allClients;
    }
    filterActions();

    $(document).on("change", "#id_selected_clients_member", function () {
        filterActions();
    });

    $(document).on("click", ".membership .btn, .membership li", function () {
        setTimeout(filterActions, 50);
    });

    $sortableLists.closest("form").submit(function (event) {
        var selectedIds = $("#actions_selected li[id]").map(function () {
            return $(this).attr('id');
        }).get();
        var idString = selectedIds.join('===');
        if (idString) { idString += '==='; }
        $('#id_actions').val(idString);
    });
}

if (typeof horizon !== 'undefined') {
    horizon.addInitFunction(function () {
        initJobsSortable();
    });
    if (horizon.modals && typeof horizon.modals.addModalInitFunction === 'function') {
        horizon.modals.addModalInitFunction(function (modal) {
            initJobsSortable();
        });
    }
} else {
    $(function () {
        initJobsSortable();
    });
}

$(document).on("show.bs.modal new_modal", ".modal", function () {
    initJobsSortable();
});
