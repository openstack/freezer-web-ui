# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

from django import shortcuts
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import tables
from django.core.urlresolvers import reverse

import disaster_recovery.api.api as freezer_api


class DeleteAction(tables.DeleteAction):
    help_text = _("Delete actions is not recoverable.")

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Action",
            u"Delete Actions",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Action",
            u"Deleted Actions",
            count
        )

    def delete(self, request, action_id):
        freezer_api.Action(request).delete(action_id)
        # TODO(m3m0): this shouldnt redirect here when an action is deleted
        # from jobs views
        return shortcuts.redirect('horizon:disaster_recovery:actions:index')


class DeleteMultipleActions(DeleteAction):
    name = "delete_multiple_actions"


class Filter(tables.FilterAction):
    filter_type = "server"
    filter_choices = (("exact", "Exact text", True),)


class CreateAction(tables.LinkAction):
    name = "create_action"
    verbose_name = _("Create Action")
    url = "horizon:disaster_recovery:actions:create"
    classes = ("ajax-modal",)
    icon = "plus"


class EditAction(tables.LinkAction):
    name = "edit_action"
    verbose_name = _("Edit")
    classes = ("ajax-modal",)
    icon = "pencil"

    def get_link_url(self, datum=None):
        return reverse("horizon:disaster_recovery:actions:create",
                       kwargs={'action_id': datum.action_id})


def get_link(action):
    return reverse('horizon:disaster_recovery:actions:action',
                   kwargs={'action_id': action.id})


class UpdateRow(tables.Row):
    ajax = True


class ActionsTable(tables.DataTable):
    backup_name = tables.Column('backup_name',

                                verbose_name=_("Action Name"),
                                link=get_link)
    action = tables.Column('action', verbose_name=_("Action"))
    path_to_backup = tables.Column('path_to_backup',
                                   verbose_name=_("Path To Backup or Restore"))
    storage = tables.Column('storage', verbose_name=_("Storage"))
    mode = tables.Column('mode', verbose_name=_("Mode"))

    def get_object_display(self, action):
        return action.backup_name

    class Meta:
        name = "actions_table"
        verbose_name = _("Actions")
        row_actions = (EditAction, DeleteAction,)
        table_actions = (Filter, CreateAction, DeleteMultipleActions)
        multi_select = True
        row_class = UpdateRow
