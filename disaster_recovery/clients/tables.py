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

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import tables
from django.core.urlresolvers import reverse

import disaster_recovery.api.api as freezer_api
from disaster_recovery.utils import shield


class Filter(tables.FilterAction):
    filter_type = "server"
    filter_choices = (("exact", "Exact text", True),)


class DeleteClient(tables.DeleteAction):
    name = "delete"
    classes = ("btn-danger",)
    icon = "remove"
    help_text = _("Delete Clients is not recoverable.")

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Client",
            u"Delete Clients",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Client",
            u"Deleted Clients",
            count
        )

    @shield("Unable to delete client", redirect="clients:index")
    def delete(self, request, client_id):
        return freezer_api.Client(request).delete(client_id)


class DeleteMultipleClients(DeleteClient):
    name = "delete_multiple_clients"


def get_link(client):
    return reverse('horizon:disaster_recovery:clients:client',
                   kwargs={'client_id': client.id})


class ClientsTable(tables.DataTable):
    client_id = tables.Column('client_id', verbose_name=_("Client ID"),
                              link=get_link)
    name = tables.Column('hostname', verbose_name=_("Hostname"))

    class Meta:
        name = "clients"
        verbose_name = _("Clients")
        row_actions = (DeleteClient,)
        table_actions = (Filter, DeleteMultipleClients,)
        multi_select = True
