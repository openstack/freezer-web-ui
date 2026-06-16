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

from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import generic

from horizon import tables

import freezer_ui.api.api as freezer_api

from freezer_ui.clients import tables as freezer_tables
from freezer_ui.utils import shield


class IndexView(tables.DataTableView):
    name = _("Clients")
    slug = "freezer-clients"
    table_class = freezer_tables.ClientsTable
    template_name = "project/freezer-clients/index.html"

    @shield('Unable to get clients', redirect='freezer-clients:index')
    def get_data(self):
        filters = self.table.get_filter_string() or None
        return freezer_api.Client(self.request).list(search=filters)


class ClientView(generic.TemplateView):
    template_name = 'project/freezer-clients/detail.html'

    @shield('Unable to get client', redirect='freezer-clients:index')
    def get_context_data(self, **kwargs):
        client_api = freezer_api.Client(self.request)
        client = client_api.get(kwargs['client_id'], json=True)
        client_info = client.get('client', {})
        client_obj = client_api.to_object(client)
        table = freezer_tables.ClientsTable(self.request)
        actions = table.render_row_actions(client_obj)
        return {
            'client': client,
            'page_title': (client_info.get('hostname') or
                           client_info.get('client_id')),
            'actions': actions,
            'url': reverse('horizon:project:freezer-clients:index')
        }
